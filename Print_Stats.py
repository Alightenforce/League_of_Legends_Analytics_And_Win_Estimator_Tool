import os
from dotenv import load_dotenv

class Print_Stats:

    load_dotenv()
    API_KEY = os.getenv("RIOT_API_KEY")

    def print_player_data(self, player):
        print("--------------------")
        print(f"PUUID: {player.puuid}")
        print(f"Level: {player.summoner_level}")
        print(f"Name: {player.summoner_name}")
        print(f"Tag: {player.summoner_tag}")
        print(f"Region: {player.region}")
        print(f"Region Code: {player.region_code}")
        print(f"Profile Picture ID: {player.pfp_id}")
        print(f"Count: {player.count}")
        print(f"Version Number: {player.version_number}")
        print("--------------------")

    def print_win_rate(self, summoner_name, win_rate, match_count):
        print("--------------------")
        print("Player's winrate: ")
        print(f"{summoner_name}'s win rate is {win_rate}% over the past {match_count} matches")
        print("--------------------")

    def print_players_champion_masteries(self, mastery_dict):
        print("--------------------")
        print("All player's mastery: ")
        for name, points in mastery_dict:
            print(f"{name}: {points}")
        print("--------------------")

    def print_side_bans(self, side_bans):
        print("--------------------")
        print("Blue side bans:")
        for champion in side_bans.get("blue_side", []):
            print(champion)
        print ("")
        print("Red side bans:")
        for champion in side_bans.get("red_side", []):
            print(champion)
        print("--------------------")

    def print_win_rate_per_champion(self, summoner_name, count, win_rate_per_champion):
        print("--------------------")
        print(f"{summoner_name}'s win rate per champion over the last {count} games:")
        for champion_name, data in win_rate_per_champion.items():
            print(f"{champion_name}: {data['Win_Rate']}% over {data['Total_Matches']} game(s)")
        print("--------------------")

    def print_average_kda_per_champion(self, summoner_name, count, average_kda_per_champion):
        print("--------------------")
        print(f"{summoner_name}'s average KDA per champion over the last {count} games:")
        for champion_name, data in average_kda_per_champion.items():
            print(f"{champion_name}: {data['Avg_KDA']} KDA | {data['Avg_Kills']}/{data['Avg_Deaths']}/{data['Avg_Assists']}")
        print("--------------------")

    def print_champions_in_current_match(self, players_in_current_game_dict):
        for team, data_list in players_in_current_game_dict.items():
            if team == "blue_team":
                print("--------------------")
                print("Blue Team: ")
                for puuid, data in data_list.items():
                    print (f"Username: {data['username']} | Champion Name: {data['champion_name']}")
                print("--------------------")
            else:
                print("--------------------")
                print ("Red team: ")
                for puuid, data in data_list.items():
                    print(f"Username: {data['username']} | Champion: {data['champion_name']}")
                print("--------------------")

    def print_live_player_champion(self, champion_name):
        print (f"Player's current champion: {champion_name}")

    def print_win_rate_with_certain_teammates(self, allies_dict):
        print("--------------------")
        choice = input("Show only >1 match? (y or n): ")
        print ("Your winrate with these teammates are: ")
        for name, stats in allies_dict.items():
            winrate = stats["winrate"]
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            if choice == "y":
                if total_matches > 1:
                    print(f"{name}: {winrate}% over {total_matches} matche(s) ({wins}W, {losses}L)")
                else:
                    continue
            else:
                print(f"{name}: {winrate}% over {total_matches} matche(s) ({wins}W, {losses}L)")
        print("--------------------")

    def print_win_rate_of_enemies_against_player(self, enemies_dict):
        print("--------------------")
        choice = input("Show only >1 match? (y or n): ")
        print ("The enemy players' winrate against you are: ")
        for name, stats in enemies_dict.items():
            winrate = stats["winrate"]
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            if choice == "y":
                if total_matches > 1:
                    print(f"{name}: {winrate}% over {total_matches} match(es) ({wins}W, {losses}L)")
                else:
                    continue
            else:
                print(f"{name}: {winrate}% over {total_matches} match(es) ({wins}W, {losses}L)")
        print("--------------------")

    def print_win_rate_with_all_ally_champions(self, win_rate_with_all_ally_champions: dict, total_matches_wanted : int):
        print("--------------------")
        print (f"Your winrate with these ally champions are: (in {total_matches_wanted} matches)")
        for name, stats in win_rate_with_all_ally_champions.items():
            winrate = stats["winrate"]
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            print (f"{name} has a {winrate}% win rate ({wins}W, {losses}L) over {total_matches} matches")
        print("--------------------")

    def print_win_rate_of_enemy_champions_against_player(self, win_rate_of_enemy_champions_against_player: dict, total_matches_wanted : int):
        print("--------------------")
        print (f"The enemy champions' winrate against you are: (in {total_matches_wanted} matches)")
        for name, stats in win_rate_of_enemy_champions_against_player.items():
            winrate = stats["winrate"]
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            print (f"{name} has a {winrate}% win rate ({wins}W, {losses}L) over {total_matches} matches")
        print("--------------------")

    def print_win_rate_of_player_against_enemy_champion(self, win_rate_of_enemy_champions_against_player: dict, total_matches_wanted : int):
        print("--------------------")
        print (f"Your winrate against these enemy champions are: (in {total_matches_wanted} matches)")
        for name, stats in win_rate_of_enemy_champions_against_player.items():
            winrate = stats["winrate"]
            wins = stats["wins"]
            losses = stats["losses"]
            total_matches = stats["total_matches"]
            player_win_rate = round(100-winrate, 2)
            print (f"{name} has a {player_win_rate}% win rate ({losses}W, {wins}L) over {total_matches} matches")
        print("--------------------")

    def print_all_masteries_in_live_match(self, team_to_puuid_to_stats: dict):
        print("--------------------------------------------------")
        for team_key, team_label in [
            ("blue_team", "Blue Team"),
            ("red_team", "Red Team"),
        ]:
            print(f"{team_label} Masteries:")
            players = team_to_puuid_to_stats.get(team_key, {})

            for puuid, stats in players.items():
                username = stats.get("username", "Unknown")
                champ_name = stats.get("champion_name", "Unknown")
                mastery = stats.get("mastery", 0)
                rank = stats.get("x_most_played")
                print(
                    f"• {username} ({champ_name}): {mastery:,} pts (#{rank} most played)"
                )
            print("--------------------------------------------------")
