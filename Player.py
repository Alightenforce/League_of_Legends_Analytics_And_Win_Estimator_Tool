import os
from dotenv import load_dotenv
import logging

from Lobby_Manager import Lobby_Manager
from Live_Match_Manager import Live_Match_Manager
from Champion_Stats_Manager import Champion_Stats_Manager
from Champion_Manager import Champion_Manager
from Mastery_Manager import Mastery_Manager
from Match_History_Manager import Match_History_Manager


from Riot_API import Riot_API
from Print_Stats import Print_Stats

load_dotenv()
logger = logging.getLogger(__name__)

class Player:

    def __init__(self, summoner_name, summoner_tag, region, total_matches_wanted):

        self.puuid = None
        self.region_code = None
        self.summoner_level = None
        self.pfp_id = None

        self.version_number = None

        self.api = Riot_API()
        self.print_stats= Print_Stats()
        self.total_matches_wanted = total_matches_wanted

        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.region = region

        self.update_profile()

        self.champion_manager = Champion_Manager(self.api, self.version_number)
        self.match_history_manager = Match_History_Manager(self.api, self.region, self.puuid, self.summoner_name, self.summoner_tag, self.total_matches_wanted)
        self.mastery_manager = Mastery_Manager(self.api, self.region_code, self.puuid, self.champion_manager)
        self.champions_stats_manager = Champion_Stats_Manager(self.match_history_manager)
        self.live_match_manager = Live_Match_Manager(self.api, self.region_code, self.puuid, self.summoner_name, self.summoner_tag, self.champion_manager)
        self.lobby_manager = Lobby_Manager(self.puuid, self.match_history_manager, self.champion_manager, self.live_match_manager)

    def update_profile(self):
        self.puuid = self.api.get_account_data(self.region, self.summoner_name, self.summoner_tag)["puuid"]
        self.region_code = self.api.get_region_data(self.region, self.puuid)["region"]
        data = self.api.get_summoner_data(self.region_code, self.puuid)
        self.summoner_level = data["summonerLevel"]
        self.pfp_id = data["profileIconId"]
        self.version_number = self.api.get_most_recent_version()