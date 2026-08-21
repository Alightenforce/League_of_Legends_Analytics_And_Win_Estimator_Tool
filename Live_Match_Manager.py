import logging
from Riot_API import RiotAPIError
from constants import *

logger = logging.getLogger(__name__)

class Live_Match_Manager:
    def __init__(self, api, region_code, puuid, summoner_name, summoner_tag, champion_manager):
        self.api = api
        self.region_code = region_code
        self.puuid = puuid
        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.champion_manager = champion_manager

    def get_all_player_info_in_live_match(self) -> dict:
        player_info_dict = {}
        try:
            data = self.api.get_active_game(self.region_code, self.puuid)
        except RiotAPIError as err:
            if err.status_code == 404:
                logger.info("No active game found.")
                return {}
            raise
        # print (data)
        participants = data["participants"]
        for index, participant in enumerate(participants):
            puuid = participant["puuid"]
            if puuid:
                player_key = puuid
            else:
                player_key = f"Streamer_Mode_{index}"

            player_info_dict[player_key] = {
                "puuid" : participant["puuid"],
                "riot_id": participant["riotId"],
                "champion_id": participant["championId"],
                "team_id": participant["teamId"]
            }
        return player_info_dict

    def sort_current_match_champions_into_teams(self, player_info_dict : dict) -> dict:
        teams = {"blue_team" : {} , "red_team" : {}}
        for puuid, data in player_info_dict.items():
            if data["team_id"] == BLUE_SIDE_ID:
                teams["blue_team"][puuid] = data
            else:
                teams["red_team"][puuid] = data
        return teams

    def sort_team_to_player_name_and_champion_in_live_match(self, player_info_dict : dict):
        player_info_dict = self.sort_current_match_champions_into_teams(player_info_dict)
        dict_of_champions = self.champion_manager.find_champion_ids_to_names()
        team_to_player_name_and_champion_dict = {"blue_team" : {} , "red_team" : {}}
        for team, players_in_team in player_info_dict.items():
            for puuid, data in players_in_team.items():
                champion_id = data["champion_id"]
                username = data["riot_id"]
                champion_name = dict_of_champions[champion_id]
                team_to_player_name_and_champion_dict[team][puuid] = {
                    "username": username,
                    "champion_name": champion_name,
                    "champion_id": champion_id
                }
        return team_to_player_name_and_champion_dict

    def get_all_masteries_in_live_match(self, live_teams = None):
        if live_teams is None:
            live_teams = self.get_champion_and_player_on_each_team_in_live_match()

        puuid_to_all_masteries = {}
        for team, players in live_teams.items():
            for puuid in players:
                if puuid.startswith("Streamer_Mode_"):
                    puuid_to_all_masteries[puuid] = []
                    continue
                try:
                    mastery_data = self.api.get_mastery_data(self.region_code, puuid)
                    puuid_to_all_masteries[puuid] = mastery_data
                except RiotAPIError:
                    logger.warning(f"No mastery data found for puuid {puuid}")
                    puuid_to_all_masteries[puuid] = []
        return puuid_to_all_masteries

    def get_live_match_champion_masteries(self):
        live_teams = self.get_champion_and_player_on_each_team_in_live_match()
        sorted_masteries = self.sort_by_player_main_champions_in_live_match(live_teams)

        team_to_puuid_to_stats = {"blue_team": {}, "red_team": {}}

        for team, players in live_teams.items():
            for puuid, player_data in players.items():
                target_champ_id = player_data["champion_id"]
                player_champ_list = sorted_masteries.get(puuid, [])
                points = 0
                x_most_played_counter = 0
                for champ in player_champ_list:
                    x_most_played_counter += 1
                    if champ["champion_id"] == target_champ_id:
                        points = champ["mastery"]
                        break

                team_to_puuid_to_stats[team][puuid] = {
                    "username": player_data["username"],
                    "champion_name": player_data["champion_name"],
                    "champion_id": target_champ_id,
                    "mastery": points,
                    "x_most_played": x_most_played_counter,
                }

        return team_to_puuid_to_stats

    # Already ordered in size of mastery so there's no need to sort
    def sort_by_player_main_champions_in_live_match(self, live_teams = None):
        if live_teams is None:
            live_teams = self.get_champion_and_player_on_each_team_in_live_match()
        puuid_to_champion_id_and_level_and_points = {}
        all_masteries = self.get_all_masteries_in_live_match(live_teams)

        for puuid, all_champion_mastery_of_current_player in all_masteries.items():
            if "status" in all_champion_mastery_of_current_player:
                puuid_to_champion_id_and_level_and_points[puuid] = []
                continue
            for champions in all_champion_mastery_of_current_player:
                if puuid not in puuid_to_champion_id_and_level_and_points:
                    puuid_to_champion_id_and_level_and_points[puuid] = []
                puuid_to_champion_id_and_level_and_points[puuid].append(
                    {
                    "champion_id": champions["championId"],
                    "mastery": champions["championPoints"],
                    "champion_level": champions["championLevel"],
                    }
                )
        return puuid_to_champion_id_and_level_and_points

    def get_champion_and_player_on_each_team_in_live_match(self) -> dict:
        live_player_info = self.get_all_player_info_in_live_match()
        return self.sort_team_to_player_name_and_champion_in_live_match(live_player_info)

    def get_live_player_champion (self) -> str:
        team_to_player_name_and_champion_dict = self.get_champion_and_player_on_each_team_in_live_match()
        for team, data_list in team_to_player_name_and_champion_dict.items():
            for data in data_list.values():
                if self.summoner_name + "#" + self.summoner_tag == data["username"]:
                    return data["champion_name"]
        return None

    def get_banned_champions_in_current_match(self) -> list:
        list_of_banned_champions_in_current_match = []
        try:
            data = self.api.get_active_game(self.region_code, self.puuid)
        except RiotAPIError as err:
            if err.status_code == 404:
                logger.info("No active game found.")
                return []
            raise
        banned_champions = data["bannedChampions"]
        for champions in banned_champions:
            champion_id_to_team = ((champions["championId"]), (champions["teamId"]))
            list_of_banned_champions_in_current_match.append(champion_id_to_team)
        return list_of_banned_champions_in_current_match

    def match_banned_champion_id_to_name(self, list_of_banned_champions_in_current_match : list) -> dict:
        dict_of_champions = self.champion_manager.find_champion_ids_to_names()
        bans_dict = {
            "blue_side" : [],
            "red_side" : []
        }
        for champion_id, team_id in list_of_banned_champions_in_current_match:
            if champion_id == -1:
                champion_name = "No ban"
            else:
                champion_name = dict_of_champions.get(champion_id, f"Champion_{champion_id}")

            if team_id == BLUE_SIDE_ID:
                bans_dict["blue_side"].append(champion_name)
            elif team_id == RED_SIDE_ID:
                bans_dict["red_side"].append(champion_name)
            else:
                raise ValueError("Team ID not found")
        return bans_dict

    def get_side_bans(self) -> dict:
        current_banned_champions_ids = self.get_banned_champions_in_current_match()
        blue_and_red_side_champion_name_bans = self.match_banned_champion_id_to_name(current_banned_champions_ids)
        return blue_and_red_side_champion_name_bans
