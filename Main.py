from Player import Player
import pandas as pd

def main():
    player1 = Player("Sinerias", "EUW", "europe", 1)
    player2 = Player("FUTA CHOGATH", "50CM", "europe", 1)
    player1.update_profile()
    player2.update_profile()
    # player1.print_win_rate()
    # player1.print_players_champion_masteries()
    # player1.print_win_rate_per_champion()
    # player1.print_average_kda_per_champion()
    # player1.print_winrate_with_allies()
    # player1.print_winrate_of_enemies_against_player()
    # player1.print_win_rate_with_all_ally_champions()
    # player1.print_win_rate_of_player_against_enemy_champion()
    # player1.print_side_bans()
    # player1.print_champions_in_current_match()
    player1.print_all_masteries_in_live_match()

if __name__ == "__main__":
    main()