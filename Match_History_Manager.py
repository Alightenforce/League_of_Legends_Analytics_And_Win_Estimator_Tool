import DB
from constants import *
import logging

logger = logging.getLogger(__name__)


class Match_History_Manager:
    def __init__(self, api, region, puuid, summoner_name, summoner_tag, total_matches_wanted):
        self.api = api
        self.region = region
        self.puuid = puuid
        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.total_matches_wanted = total_matches_wanted
        self.max_new_api_calls = MAX_NEW_API_CALLS
        self.match_history = None
        self.match_data_for_player = None

    def fetch_match_data_for_player(self):
        if self.match_data_for_player is None:
            self.match_data_for_player = self.get_player_stats_from_previous_matches()
        return self.match_data_for_player

    def get_match_history(self):
        if self.match_history is None:
            self.match_history = self.api.get_match_ids(self.region, self.puuid, self.total_matches_wanted)
        return self.match_history

    def get_player_stats_from_previous_matches(self) -> list:
        match_history = self.get_match_history()
        each_match_data_for_player = self.get_each_match_data_for_player(match_history)
        return each_match_data_for_player

    def get_win_rate(self) -> float:
        each_match_data_for_player = self.fetch_match_data_for_player()
        return self.calculate_win_rate(each_match_data_for_player)

    def get_each_match_data_for_player(self, match_history: list) -> list[list]:
        matches_data_for_player = []
        raw_matches = self.get_each_match_data(match_history)
        for data in raw_matches:
            found_player = False
            for participant in data['info']['participants']:
                if participant.get('puuid') == self.puuid:
                    matches_data_for_player.append(participant)
                    found_player = True
                    break

            # Likely corrupted game
            if not found_player:
                logger.error("Could not find player in current match: %s", data)
        return matches_data_for_player

    def get_each_match_data(self, match_history : list) -> list:
        match_data = []
        new_api_calls_made = 0
        for match_id in match_history:
            if DB.is_match_cached(match_id):
                data = DB.get_match_json(match_id)
                # print("Saving API Calls")
            elif new_api_calls_made < self.max_new_api_calls:
                data = self.api.get_match_detail(self.region, match_id)
                DB.save_match_data(self.puuid, data, self.summoner_name, self.summoner_tag, self.region)
                new_api_calls_made += 1
                # print (f"Fetching uncached match, current new API calls: {new_api_calls_made}")
            else:
                logger.error("API budget exceeded")
                continue
            match_data.append(data)
        return match_data

    def calculate_win_rate(self, each_match_data: list) -> float:
        wins = 0
        losses = 0
        for each_match in each_match_data:
            if each_match["win"]:
                wins += 1
            else:
                losses += 1
        if len(each_match_data) == 0:
            win_rate = 0
        else:
            win_rate = wins / len(each_match_data)
        win_rate_percent = win_rate * 100
        return round(win_rate_percent, 2)