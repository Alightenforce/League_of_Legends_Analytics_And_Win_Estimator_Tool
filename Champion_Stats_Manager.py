class Champion_Stats_Manager:
    def __init__(self, match_history_manager):
        self.match_history_manager = match_history_manager

    def get_player_stats_per_champion(self, match_data = None) -> dict:
        dict_of_player_stats_per_champion = {}
        if match_data is None:
            match_data = self.match_history_manager.fetch_match_data_for_player()
        for each_match in match_data:
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
            avg_kda = round((avg_kills + avg_assists) / max(1,avg_deaths), 1)

            average_kda_per_champion[name] = {"Avg_Kills" : avg_kills, "Avg_Deaths" : avg_deaths, "Avg_Assists" : avg_assists, "Avg_KDA" : avg_kda}
        return average_kda_per_champion