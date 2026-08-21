from Player import Player
from Print_Player_Stats import Print_Player_Stats
from Print_Stats import Print_Stats
from Riot_API import RiotAPIError
import logging

logger = logging.getLogger(__name__)

def main():
    try:
        player1 = Player("Doublelift", "NA01", "americas", 1)
        formatting_text = Print_Stats()
        stat_print = Print_Player_Stats(player1, formatting_text)

        # stat_print.print_win_rate()
        # stat_print.print_players_champion_masteries()
        # stat_print.print_win_rate_per_champion()
        # stat_print.print_average_kda_per_champion()
        # stat_print.print_winrate_with_allies()
        # stat_print.print_winrate_of_enemies_against_player()
        # stat_print.print_win_rate_with_all_ally_champions()
        # stat_print.print_win_rate_of_player_against_enemy_champion()

        # stat_print.print_side_bans()
        # stat_print.print_champions_in_current_match()
        # stat_print.print_live_player_champion()
        # stat_print.print_all_masteries_in_live_match()

    except RiotAPIError as err:
        print (f"Error initialising profile: {err}")
        return

if __name__ == "__main__":
    main()