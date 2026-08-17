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
        self.match_data_for_player = None
        self.match_history = None

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
        self.match_history = self.get_match_history()

    def fetch_champion_lookup(self):
        if self.champion_lookup is None:
            self.champion_lookup = self.api.get_champion_data(self.version_number)
        return self.champion_lookup

    def get_match_history(self):
        if self.match_history is None:
            self.match_history = self.api.get_match_ids(self.region, self.puuid, self.total_matches_wanted)
        return self.match_history

    def fetch_match_data_for_player(self):
        if self.match_data_for_player is None:
            self.match_data_for_player = self.get_player_stats_from_previous_matches()
        return self.match_data_for_player

    def print_player_data(self):
        self.print_stats.print_player_data(self)

    ###################################################### Win Rate ##########################################################

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
                print(f'Could not find PUUID in match {data["metadata"]["matchId"]} (Skipping)')
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
                print ("API budget exceeded, skipping remaining uncached games")
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
        win_rate = wins / len(each_match_data)
        win_rate_percent = win_rate * 100
        return round(win_rate_percent, 2)

    def print_win_rate(self):
        self.print_stats.print_win_rate(self.summoner_name, self.get_win_rate(), self.total_matches_wanted)

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

    def print_players_champion_masteries(self):
        self.print_stats.print_players_champion_masteries(self.get_champion_name_to_champion_mastery().items())


###################################################### Mastery ##########################################################

###################################################### Live Match ##########################################################
    def get_all_player_info_in_live_match(self) -> dict:
        player_info_dict = {}
        try:
            data = self.api.get_active_game(self.region_code, self.puuid)
        except:
            print("Player is not in a live game or API call failed.")
            return player_info_dict
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
        dict_of_champions = self.find_champion_ids_to_names()
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
                mastery_data = self.api.get_mastery_data(self.region_code, puuid)
                if "status" in mastery_data:
                    mastery_data = []
                puuid_to_all_masteries[puuid] = mastery_data

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

    def print_all_masteries_in_live_match(self):
        self.print_stats.print_all_masteries_in_live_match(self.get_live_match_champion_masteries())

    def get_champion_and_player_on_each_team_in_live_match(self) -> dict:
        live_player_info = self.get_all_player_info_in_live_match()
        return self.sort_team_to_player_name_and_champion_in_live_match(live_player_info)

    def print_champions_in_current_match(self):
        match_data = self.get_champion_and_player_on_each_team_in_live_match()
        self.print_stats.print_champions_in_current_match(match_data)

    def get_live_player_champion (self) -> str:
        team_to_player_name_and_champion_dict = self.get_champion_and_player_on_each_team_in_live_match()
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

    def get_player_stats_per_champion(self, match_data = None) -> dict:
        dict_of_player_stats_per_champion = {}
        if match_data is None:
            if self.match_data_for_player is None:
                self.fetch_match_data_for_player()
            match_data = self.match_data_for_player

        each_match_data = match_data
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
        self.print_stats.print_win_rate_per_champion(self.summoner_name, self.total_matches_wanted, self.calculate_win_rate_per_champion())

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
        self.print_stats.print_average_kda_per_champion(self.summoner_name, self.total_matches_wanted, self.get_average_kda_per_champion())

###################################################### Champion Specific ##########################################################

###################################################### Lobby Specific ##########################################################
    def get_all_player_info_in_previous_matches(self) -> list[dict]:
        all_matches_team_info = []
        match_history = self.get_match_history()
        matches_data = self.get_each_match_data(match_history)
        for match in matches_data:
            single_match = {}
            participants = match["info"]["participants"]
            for participant in participants:
                single_match[participant["puuid"]] = {
                    "riot_id_game_name": participant["riotIdGameName"],
                    "riot_id_tag_line": participant["riotIdTagline"],
                    "champion_id": participant["championId"],
                    "team_id": participant["teamId"],
                    "has_won": participant["win"]
                }
            all_matches_team_info.append(single_match)
        return all_matches_team_info

    def sort_all_previous_matches_into_teams(self) -> list:
        all_matches_team_info = self.get_all_player_info_in_previous_matches()
        sorted_teams = []
        for match in all_matches_team_info:
            sorted_teams.append(self.sort_current_match_champions_into_teams(match))
        return sorted_teams

    def determine_current_player_team(self, match: dict, dont_want_opposite_team: bool) -> int:
        if self.puuid in match["blue_team"] and dont_want_opposite_team:
            return BLUE_SIDE_ID
        elif self.puuid in match["blue_team"] and not dont_want_opposite_team:
            return RED_SIDE_ID
        elif self.puuid in match["red_team"] and dont_want_opposite_team:
            return RED_SIDE_ID
        elif self.puuid in match["red_team"]and not dont_want_opposite_team:
            return BLUE_SIDE_ID
        else:
            return None

    def get_players_teams_data(self) -> list:
        dont_want_opposite_team = True
        all_players_previous_teams_data = self.get_certain_teams_data(dont_want_opposite_team)
        return all_players_previous_teams_data

    def get_enemy_teams_data(self) -> list:
        dont_want_opposite_team = False
        all_enemy_previous_teams_data = self.get_certain_teams_data(dont_want_opposite_team)
        return all_enemy_previous_teams_data

    def get_certain_teams_data(self, dont_want_opposite_team: bool) -> list:
        all_previous_teams_data = []
        sorted_teams = self.sort_all_previous_matches_into_teams()
        for match in sorted_teams:
            current_players_side = self.determine_current_player_team(match, dont_want_opposite_team)
            if current_players_side == BLUE_SIDE_ID:
                team_key = "blue_team"
            elif current_players_side == RED_SIDE_ID:
                team_key = "red_team"
            else:
                continue
            team_data = match[team_key]
            all_previous_teams_data.append(team_data)
        return all_previous_teams_data

    def determine_win_rate_of_each_person(self, dont_want_opposite_team: bool) -> dict:
        current_player_history_with_players = {self.puuid: {}}
        if dont_want_opposite_team:
            all_previous_teams_data = self.get_players_teams_data()
        else:
            all_previous_teams_data = self.get_enemy_teams_data()
        for players in all_previous_teams_data:
            for puuid in players:
                if puuid == self.puuid:
                    continue
                if puuid not in current_player_history_with_players[self.puuid]:
                    current_player_history_with_players[self.puuid][puuid] = {"wins": 0, "losses": 0}
                if players[puuid]["has_won"]:
                    current_player_history_with_players[self.puuid][puuid]["wins"] += 1
                else:
                    current_player_history_with_players[self.puuid][puuid]["losses"] += 1
        return current_player_history_with_players

    def calculate_win_rate_of_each_person(self, dont_want_opposite_team: bool ) -> dict:
        teammate_puuid_to_stats = {}
        current_player_history_with_other_teammates = self.determine_win_rate_of_each_person(dont_want_opposite_team)
        for player_puuid, teammates_puuid in current_player_history_with_other_teammates.items():
            for teammate_puuid, stats in teammates_puuid.items():
                wins = stats["wins"]
                losses = stats["losses"]
                total_matches = wins + losses

                win_rate = wins / total_matches
                win_rate_percent = round(win_rate * 100, 1)
                teammate_puuid_to_stats[teammate_puuid] = {
                    "wins": wins,
                    "losses": losses,
                    "winrate": win_rate_percent,
                    "total_matches": total_matches
                }
        return teammate_puuid_to_stats

    def calculate_win_rate_of_each_person_on_team(self):
        dont_want_opposite_team = True
        teammate_puuid_to_stats = self.calculate_win_rate_of_each_person(dont_want_opposite_team)
        return teammate_puuid_to_stats

    def calculate_win_rate_of_each_person_on_enemy_team(self):
        dont_want_opposite_team = False
        enemy_puuid_to_stats = self.calculate_win_rate_of_each_person(dont_want_opposite_team)
        return enemy_puuid_to_stats

    def map_puuid_to_summoner_id(self, dont_want_opposite_team: bool) -> dict:
        puuid_to_summoner_ids = {}
        if dont_want_opposite_team:
            all_previous_teams_data = self.get_players_teams_data()
        else:
            all_previous_teams_data = self.get_enemy_teams_data()
        for player in all_previous_teams_data:
            for puuid, data in player.items():
                if puuid == self.puuid:
                    continue
                summoner_id = data["riot_id_game_name"] + "#" + data["riot_id_tag_line"]
                puuid_to_summoner_ids[puuid] = summoner_id
        return puuid_to_summoner_ids

    # Avoid using a double nested for loop by using get
    def map_summoner_id_to_stats(self, dont_want_opposite_team: bool) -> dict:
        summoner_id_to_stats = {}
        if dont_want_opposite_team:
            puuid_to_stats = self.calculate_win_rate_of_each_person_on_team()
        else:
            puuid_to_stats = self.calculate_win_rate_of_each_person_on_enemy_team()
        puuid_to_summoner_ids = self.map_puuid_to_summoner_id(dont_want_opposite_team)
        for puuid, stats in puuid_to_stats.items():
            summoner_id = puuid_to_summoner_ids.get(puuid)
            summoner_id_to_stats[summoner_id] = stats
        return summoner_id_to_stats

    def get_stats_with_allies(self):
        dont_want_opposite_team = True
        summoner_id_to_stats = self.map_summoner_id_to_stats(dont_want_opposite_team)
        return summoner_id_to_stats

    def get_stats_of_enemies_against_player(self):
        dont_want_opposite_team = False
        summoner_id_to_stats = self.map_summoner_id_to_stats(dont_want_opposite_team)
        return summoner_id_to_stats

    def print_winrate_with_allies(self):
        self.print_stats.print_win_rate_with_certain_teammates(self.get_stats_with_allies())

    def print_winrate_of_enemies_against_player(self):
        self.print_stats.print_win_rate_of_enemies_against_player(self.get_stats_of_enemies_against_player())

    def sort_champions_into_corresponding_teams(self, dont_want_opposite_team: bool) -> list[dict]:
        all_matches_team_data = self.get_certain_teams_data(dont_want_opposite_team)
        list_of_team_side_to_champion=[]
        for matches in all_matches_team_data:
            team_side_to_champion = {}
            for puuid, stats in matches.items():
                if puuid == self.puuid:
                    continue
                team_id = stats["team_id"]
                has_won = stats["has_won"]
                champion_id = stats["champion_id"]

                if team_id not in team_side_to_champion:
                    team_side_to_champion[team_id] = {
                        "has_won": has_won,
                        "champion_ids": []
                    }
                team_side_to_champion[team_id]["champion_ids"].append(champion_id)
            list_of_team_side_to_champion.append(team_side_to_champion)
        return list_of_team_side_to_champion

    def determine_win_rate_of_champion_with_or_against_player(self, dont_want_opposite_team: bool) -> dict:
        champion_id_to_winrate = {}
        list_of_team_side_to_champion = self.sort_champions_into_corresponding_teams(dont_want_opposite_team)
        for team in list_of_team_side_to_champion:
            for team_id, champion_ids_and_has_won in team.items():
                has_won = champion_ids_and_has_won["has_won"]
                champion_id_list = champion_ids_and_has_won["champion_ids"]
                for champion_id in champion_id_list:
                    if champion_id not in champion_id_to_winrate:
                        champion_id_to_winrate[champion_id] = {
                            "wins" : 0,
                            "losses" : 0,
                            "total_matches" : 0
                        }
                    if has_won:
                        champion_id_to_winrate[champion_id]["wins"] += 1
                        champion_id_to_winrate[champion_id]["total_matches"] += 1
                    else:
                        champion_id_to_winrate[champion_id]["losses"] += 1
                        champion_id_to_winrate[champion_id]["total_matches"] += 1
        return champion_id_to_winrate

    def calculate_win_rate_of_champion_with_or_against_player(self, dont_want_opposite_team: bool) -> dict:
        champion_id_to_winrate = self.determine_win_rate_of_champion_with_or_against_player(dont_want_opposite_team)
        for champion_id, stats in champion_id_to_winrate.items():
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            win_rate = wins / total_matches
            win_rate_percent = round(win_rate * 100, 1)
            champion_id_to_winrate[champion_id] ={
                "wins" : wins,
                "losses" : losses,
                "winrate" : win_rate_percent,
                "total_matches" : total_matches
            }
        return champion_id_to_winrate

    def map_champion_id_to_name_for_previous_matches(self, dont_want_opposite_team: bool) -> dict:
        champion_name_to_stats = {}
        champion_id_to_stats = self.calculate_win_rate_of_champion_with_or_against_player(dont_want_opposite_team)
        dictionary_of_champion_ids_and_names = self.find_champion_ids_to_names()
        for champion_id, stats in champion_id_to_stats.items():
            champion_name = dictionary_of_champion_ids_and_names[champion_id]
            champion_name_to_stats[champion_name] = stats
        return champion_name_to_stats

    def determine_win_rate_of_enemy_champions_against_player(self):
        dont_want_opposite_team = False
        win_rate_of_enemy_champions_against_player = self.map_champion_id_to_name_for_previous_matches(dont_want_opposite_team)
        return win_rate_of_enemy_champions_against_player

    def determine_win_rate_with_all_ally_champions(self):
        dont_want_opposite_team = True
        win_rate_with_ally_champions = self.map_champion_id_to_name_for_previous_matches(dont_want_opposite_team)
        return win_rate_with_ally_champions

    def print_win_rate_with_all_ally_champions(self):
        self.print_stats.print_win_rate_with_all_ally_champions(self.determine_win_rate_with_all_ally_champions(), self.total_matches_wanted)

    def print_win_rate_of_enemy_champions_against_player(self):
        self.print_stats.print_win_rate_of_enemy_champions_against_player(self.determine_win_rate_of_enemy_champions_against_player(), self.total_matches_wanted)

    def print_win_rate_of_player_against_enemy_champion(self):
        self.print_stats.print_win_rate_of_player_against_enemy_champion(self.determine_win_rate_of_enemy_champions_against_player(), self.total_matches_wanted)

    ###################################################### Lobby Specific ##########################################################

    def display_summoner_pfp_img(self):
        page = self.api.get_account_data(self.region_code, self.summoner_name, self.summoner_tag)
        img = Image.open(BytesIO(page.content))
        buffer = BytesIO() # Puts it into RAM
        img.save(buffer, format="PNG") # Put image data into virtual container in RAM
        buffer.seek(0) # Move head back to start after writing
        output = climage.convert(buffer, is_unicode=True, width = 40)
        print(output)

