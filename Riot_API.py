import requests
import os
from dotenv import load_dotenv
import logging

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

logging.basicConfig(
    level=logging.INFO, # Has 5 severity levels: DEBUG, INFO, WARNING, ERROR, CRITICAL - it ignores DEBUG
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s", # Stores the timestamp, the severity level, the name of the module, the full message text parsed to the logger (the % are formatters and s stands for string like in c)
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Create custom exception handling
class RiotAPIError(Exception):
    def __init__(self, message, status_code=None):
        super().__init__(message) # Calls the parent constructor (Exception) and passes the message variable into the parent class to deal with
        self.status_code = status_code

class Riot_API:

    def __init__(self):
        self.api_key = API_KEY
        self.session = requests.Session()

    def get_account_data(self, region: str, name: str, tag: str):
        link = f"https://{region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{name}/{tag}?api_key={self.api_key}"
        return self.get_json(link)

    def get_region_data(self, region: str, puuid : str):
        link = f"https://{region}.api.riotgames.com/riot/account/v1/region/by-game/lol/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_summoner_data(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_match_ids(self, region: str, puuid: str, total_matches_wanted: int = 100) -> list[str]:
        all_match_ids = []
        # Calculate number of pages
        for start_index in range(0, total_matches_wanted, 100):

            # Calculate the remaining on the page
            current_count = min(100, total_matches_wanted - len(all_match_ids))

            link = (
                f'https://{region}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids'
                f'?start={start_index}&count={current_count}&api_key={self.api_key}'
            )

            page_ids = self.get_json(link)

            # Player doesn't have enough matches in their history
            if not page_ids or not isinstance(page_ids, list):
                break

            all_match_ids.extend(page_ids)

            # Riot stop returning the player's history
            if len(page_ids) < current_count:
                break

        return all_match_ids

    def get_match_detail(self, region: str, match_id: str):
        link = f"https://{region}.api.riotgames.com/lol/match/v5/matches/{match_id}?api_key={self.api_key}"
        return self.get_json(link)

    def get_mastery_data(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_active_game(self, region_code: str, puuid: str):
        link = f"https://{region_code}.api.riotgames.com/lol/spectator/v5/active-games/by-summoner/{puuid}?api_key={self.api_key}"
        return self.get_json(link)

    def get_json(self, link : str):
        try:
            response = self.session.get(link, timeout=(3.05, 10)) # TCP packets are retransmitted at integer intervals, so making it slightly above a 3 ensures it can restransmit. The structure (3.05, 10) means 3.05 seconds wait time to establish a connection to the RIOT servers and 10 seconds for RIOT to send the information back to the program
            app_calls = response.headers.get("X-App-Rate-Limit-Count")
            print(f"[Riot API Usage] -> {app_calls}")
            response.raise_for_status() # Since python treats any response as valid, I need to raise for status to actually see if it's an error or valid data
            return response.json()

        # Checks for timeouts
        except requests.exceptions.Timeout:
            logger.error("Request timed out while connecting or reading from %s", link)
            raise RiotAPIError("Request timed out while contacting Riot servers.")

        # Checks for an error code 4xx or 5xx and status_code extracts the error code from raw response object
        except requests.exceptions.HTTPError as exc:
            status_code = exc.response.status_code
            # Expired API Key
            if status_code == 401 or status_code == 403:
                logger.critical("Riot API key is expired. Please get a new key at https://developer.riotgames.com/")
                raise RiotAPIError(f"HTTP {status_code}: Riot API key is expired or invalid.", status_code=status_code)
            # Rate limit exceeded
            elif status_code == 404:
                logger.warning("Information not found at %s", link)
                raise RiotAPIError("HTTP 404: Resource not found.", status_code=status_code)
            elif status_code == 429:
                logger.critical("Rate limit exceeded")
                raise RiotAPIError("HTTP 429: Rate limit exceeded.", status_code=status_code)
            else:
                logger.error("HTTP %s Error: %s", status_code, exc.response.text)
                raise RiotAPIError(f"HTTP {status_code} Error from Riot API.", status_code=status_code)

        # Checks to determine whether I could reach Riot servers at all
        except requests.exceptions.ConnectionError:
            logger.error("Network connection failed.")
            raise RiotAPIError("Network connection failed.")

        # Checks to ensure Riot returned valid JSON, only returns the first 200 characters in case loads of stuff is returned
        except requests.exceptions.JSONDecodeError:
            if response is not None:
                raw_text = response.text[:200]
            else:
                raw_text = "No response"
            logger.error("Failed to decode JSON payload. Response was: %s", raw_text)
            raise RiotAPIError("Invalid JSON received from Riot API.")

        # Checks for unexpected errors
        except requests.exceptions.RequestException as exc:
            logger.error("An unexpected request error occurred: %s", exc)
            raise RiotAPIError(f"Unexpected network error: {exc}")

    def get_most_recent_version(self):
        link = "https://ddragon.leagueoflegends.com/api/versions.json"
        versions = self.get_json(link)
        return versions[0]

    def get_champion_data(self, version: str):
        link = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        return self.get_json(link)


