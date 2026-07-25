from Player import Player

def main():
    player1 = Player("Alightenforce", "4040", "europe", 300)
    player1.update_profile()
    # player1.print_win_rate_of_enemy_champions_against_player()
    player1.print_win_rate_with_all_ally_champions()
    player1.print_win_rate_of_player_against_enemy_champion()

if __name__ == "__main__":
    main()