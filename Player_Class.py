# TO DO
# CYCLE THROUGH PREVIOUS MATCHES
# MAKE A TALLY OF W/L AGAINST CERTAIN CHAMPIONS, AGAINST CERTAIN PEOPLE AND WITH CERTAIN PEOPLE

import requests
import os
from dotenv import load_dotenv
import json
import time
import climage
from PIL import Image
from io import BytesIO

import DB
from Riot_API import Riot_API
from Print_Stats import Print_Stats
from pyarrow.types import is_unicode

load_dotenv()
API_KEY = os.getenv("RIOT_API_KEY")

BLUE_SIDE_ID = 100
RED_SIDE_ID = 200
MAX_NEW_API_CALLS = 50

class Player:

    def __init__(self, summoner_name, summoner_tag, region, total_matches_wanted, max_new_api_calls = MAX_NEW_API_CALLS):

        self.puuid = None
        self.region_code = None
        self.summoner_level = None
        self.pfp_id = None

        self.version_number = None
        self.champion_lookup = None
        self.match_data = None

        self.api = Riot_API()
        self.print_stats= Print_Stats()
        self.total_matches_wanted = total_matches_wanted
        self.max_new_api_calls = max_new_api_calls

        self.summoner_name = summoner_name
        self.summoner_tag = summoner_tag
        self.region = region
        # self.count = count

    def update_profile(self):
        self.puuid = self.api.get_account_data(self.region, self.summoner_name, self.summoner_tag)["puuid"]
        self.region_code = self.api.get_region_data(self.region, self.puuid)["region"]
        data = self.api.get_summoner_data(self.region_code, self.puuid)
        self.summoner_level = data["summonerLevel"]
        self.pfp_id = data["profileIconId"]
        self.version_number = self.api.get_most_recent_version()

    def fetch_champion_lookup(self):
        if self.champion_lookup is None:
            self.champion_lookup = self.api.get_champion_data(self.version_number)
        return self.champion_lookup

    def fetch_match_data(self):
        if self.match_data is None:
            self.match_data = self.get_player_stats_from_previous_matches()
        return self.match_data

    def print_player_data(self):
        self.print_stats.print_player_data(self)

    ###################################################### Win Rate ##########################################################

    def get_player_stats_from_previous_matches(self) -> list:
        data = self.api.get_match_ids(self.region, self.puuid, self.total_matches_wanted)
        each_match_data_for_player = self.get_each_match_data_for_player(data)
        return each_match_data_for_player

    def get_win_rate(self) -> float:
        each_match_data_for_player = self.fetch_match_data()
        return self.calculate_win_rate(each_match_data_for_player)

    def get_each_match_data_for_player(self, match_history: list) -> list[list]:
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
                print (f"Fetching uncached match, current new API calls: {new_api_calls_made}")
            else:
                print ("API budget exceeded, skipping remaining uncached games")
                continue
            found_player = False
            for participant in data['info']['participants']:
                if participant.get('puuid') == self.puuid:
                    match_data.append(participant)
                    found_player = True
                    break

            # Likely corrupted game
            if not found_player:
                print(f'Could not find PUUID in match {match_id} (Skipping)')

        return match_data

    def calculate_win_rate(self, each_match_data: list) -> float:
        wins = 0
        losses = 0
        for each_match in each_match_data:
            if each_match["win"]:
                wins += 1
            else:
                losses += 1
        win_rate = wins / len(each_match_data)
        win_rate_percent = win_rate * 100
        return round(win_rate_percent, 2)

    def print_win_rate(self):
        self.print_stats.print_win_rate(self.summoner_name, self.get_win_rate(), len(self.match_data))

###################################################### Win Rate ##########################################################

###################################################### Mastery ##########################################################
    # Dictionary uses O(1) over a list which would use O(n)
    def find_champion_ids_to_names(self) -> dict:
        dict_of_champion_ids_to_names = {}
        data = self.api.get_champion_data(self.version_number)
        all_champion_names = data["data"]
        for champion in all_champion_names.values():
            dict_of_champion_ids_to_names[int((champion["key"]))] = champion["name"]
        return dict_of_champion_ids_to_names

    def get_all_champion_masteries(self) -> list:
        list_of_champion_masteries = []
        data = self.api.get_mastery_data(self.region_code, self.puuid)
        for champion in data:
            id_to_mastery = ((champion["championId"]), (champion["championPoints"]))
            list_of_champion_masteries.append(id_to_mastery)
        return list_of_champion_masteries

    def match_champion_name_to_champion_mastery(self, list_of_champion_masteries : list, dict_of_champion_ids_to_names : dict) -> dict:
        champion_name_to_champion_mastery = {}
        for champion_id_mastery, mastery_points in list_of_champion_masteries:
            if champion_id_mastery in dict_of_champion_ids_to_names:
                champion_name = (dict_of_champion_ids_to_names[champion_id_mastery])
                champion_name_to_champion_mastery[champion_name] = mastery_points
        return champion_name_to_champion_mastery

    def get_champion_name_to_champion_mastery(self) -> dict:
        list_of_champion_masteries = self.get_all_champion_masteries()
        dictionary_of_champion_ids_and_names = self.find_champion_ids_to_names()
        name_to_mastery_points = self.match_champion_name_to_champion_mastery(list_of_champion_masteries, dictionary_of_champion_ids_and_names)
        return name_to_mastery_points

    def print_champion_name_to_champion_mastery(self):
        self.print_stats.print_champion_name_to_champion_mastery(self.get_champion_name_to_champion_mastery().items())

###################################################### Mastery ##########################################################

###################################################### Live Match ##########################################################
    def get_all_player_info_in_current_match(self) -> dict:
        player_info_dict = {}
        data = self.api.get_active_game(self.region_code, self.puuid)
        participants = data["participants"]
        for participant in participants:
            player_info_dict[participant["puuid"]] = {
                "riot_id": participant["riotId"],
                "champion_id": participant["championId"],
                "team_id": participant["teamId"]
            }
        return player_info_dict

    def sort_current_match_champions_into_teams(self) -> dict:
        player_info_dict = self.get_all_player_info_in_current_match()
        teams = {"blue_team" : [] , "red_team" : []}
        for puuid, data in player_info_dict.items():
            if data["team_id"] == BLUE_SIDE_ID:
                teams["blue_team"].append(data)
            else:
                teams["red_team"].append(data)
        return teams


    def get_champion_and_player_on_each_team_in_current_match(self) -> dict:
        player_info_dict = self.sort_current_match_champions_into_teams()
        dict_of_champions = self.find_champion_ids_to_names()
        team_to_player_name_and_champion_dict = {"blue_team" : [] , "red_team" : []}
        for team, data_list in player_info_dict.items():
            for data in data_list:
                champion_id = data["champion_id"]
                username = data["riot_id"]
                champion_name = dict_of_champions[champion_id]
                player_pairing = {
                    "username": username,
                    "champion_name": champion_name
                }

                team_to_player_name_and_champion_dict[team].append(player_pairing)

        return team_to_player_name_and_champion_dict

    def print_champions_in_current_match(self):
        match_data = self.get_champion_and_player_on_each_team_in_current_match()
        self.print_stats.print_champions_in_current_match(match_data)

    def get_live_player_champion (self) -> str:
        team_to_player_name_and_champion_dict = self.get_champion_and_player_on_each_team_in_current_match()
        for team, data_list in team_to_player_name_and_champion_dict.items():
            for data in data_list:
                if self.summoner_name + "#" + self.summoner_tag == data["username"]:
                    return data["champion_name"]
        raise ValueError("Champion not found")

    def print_live_player_champion(self):
        my_champion = self.get_live_player_champion()
        self.print_stats.print_live_player_champion(my_champion)

    def get_banned_champions_in_current_match(self) -> list:
        list_of_banned_champions_in_current_match = []
        data = self.api.get_active_game(self.region_code, self.puuid)
        banned_champions = data["bannedChampions"]
        for champions in banned_champions:
            champion_id_to_team = ((champions["championId"]), (champions["teamId"]))
            list_of_banned_champions_in_current_match.append(champion_id_to_team)
        return list_of_banned_champions_in_current_match

    def match_banned_champion_id_to_name(self, list_of_banned_champions_in_current_match : list) -> dict:
        dict_of_champions = self.find_champion_ids_to_names()
        bans_dict = {
            "blue_side" : [],
            "red_side" : []
        }
        for champion_id, team_id in list_of_banned_champions_in_current_match:
            if champion_id == -1:
                champion_name = "No ban"
            else:
                champion_name = dict_of_champions[champion_id]
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

    def print_side_bans(self):
        self.print_stats.print_side_bans(self.get_side_bans())

###################################################### Live Match ##########################################################

###################################################### Champion Specific ##########################################################

    def get_player_stats_per_champion(self) -> dict:
        dict_of_player_stats_per_champion = {}
        if self.match_data is None:
            self.fetch_match_data()
        each_match_data = self.match_data

        for each_match in each_match_data:
            champion_name = each_match["championName"]
            kills = each_match["kills"]
            deaths = each_match["deaths"]
            assists = each_match["assists"]
            win = each_match["win"]
            if champion_name not in dict_of_player_stats_per_champion:
                dict_of_player_stats_per_champion[champion_name] = {"Wins" : 0, "Losses" : 0, "Kills" : 0, "Deaths" : 0, "Assists" : 0, "Games" : 0}
            if win:
                dict_of_player_stats_per_champion[champion_name]["Wins"] += 1
            else:
                dict_of_player_stats_per_champion[champion_name]["Losses"] += 1
            dict_of_player_stats_per_champion[champion_name]["Kills"] += kills
            dict_of_player_stats_per_champion[champion_name]["Deaths"] += deaths
            dict_of_player_stats_per_champion[champion_name]["Assists"] += assists
            dict_of_player_stats_per_champion[champion_name]["Games"] += 1
        return dict_of_player_stats_per_champion

    def calculate_win_rate_per_champion(self) -> dict:
        win_rate_per_champion = {}
        player_stats_per_champion = self.get_player_stats_per_champion()
        for name, stats in player_stats_per_champion.items():
            wins = stats["Wins"]
            games = stats["Games"]
            win_rate = wins / games
            win_rate_per_champion[name] = {"Win_Rate" : round(win_rate * 100, 2), "Total_Matches" : games}
        return win_rate_per_champion

    def print_win_rate_per_champion(self):
        self.print_stats.print_win_rate_per_champion(self.summoner_name, len(self.match_data), self.calculate_win_rate_per_champion())

    def get_average_kda_per_champion(self) -> dict:
        average_kda_per_champion = {}
        player_stats_per_champion = self.get_player_stats_per_champion()
        for name, stats in player_stats_per_champion.items():
            kills = stats["Kills"]
            deaths = stats["Deaths"]
            assists = stats["Assists"]
            games = stats["Games"]

            if deaths == 0:
                deaths = 1

            avg_kills = round((kills / games), 1)
            avg_deaths = round((deaths / games), 1)
            avg_assists = round((assists / games), 1)
            avg_kda = round((avg_kills + avg_assists) / avg_deaths, 1)

            average_kda_per_champion[name] = {"Avg_Kills" : avg_kills, "Avg_Deaths" : avg_deaths, "Avg_Assists" : avg_assists, "Avg_KDA" : avg_kda}
        return average_kda_per_champion

    def print_average_kda_per_champion(self):
        self.print_stats.print_average_kda_per_champion(self.summoner_name, len(self.match_data), self.get_average_kda_per_champion())

###################################################### Champion Specific ##########################################################

    def display_summoner_pfp_img(self):
        page = self.api.get_account_data(self.region_code, self.summoner_name, self.summoner_tag)
        img = Image.open(BytesIO(page.content))
        buffer = BytesIO() # Puts it into RAM
        img.save(buffer, format="PNG") # Put image data into virtual container in RAM
        buffer.seek(0) # Move head back to start after writing
        output = climage.convert(buffer, is_unicode=True, width = 40)
        print(output)
