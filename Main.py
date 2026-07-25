from Player import Player

def main():
    player1 = Player("Thebausffs", "COOL", "europe", 1)
    player1.update_profile()
    player1.print_all_masteries_in_live_match()
if __name__ == "__main__":
    main()