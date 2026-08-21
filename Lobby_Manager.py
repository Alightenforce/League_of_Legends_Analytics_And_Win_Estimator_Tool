from constants import *

class Lobby_Manager:
    def __init__(self, puuid, match_history_manager, champion_manager, live_match_manager):
        self.puuid = puuid
        self.match_history_manager = match_history_manager
        self.champion_manager = champion_manager
        self.live_match_manager = live_match_manager

    def get_all_player_info_in_previous_matches(self) -> list[dict]:
        all_matches_team_info = []
        match_history = self.match_history_manager.get_match_history()
        matches_data = self.match_history_manager.get_each_match_data(match_history)
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
            sorted_teams.append(self.live_match_manager.sort_current_match_champions_into_teams(match))
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
                if total_matches == 0:
                    win_rate = 0
                else:
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
            if total_matches == 0:
                win_rate = 0
            else:
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
        dictionary_of_champion_ids_and_names = self.champion_manager.find_champion_ids_to_names()
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