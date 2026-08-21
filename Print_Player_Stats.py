class Print_Player_Stats:
    def __init__(self, player, print_stats):
        self.player = player
        self.print_stats = print_stats

    def print_player_data(self):
        self.print_stats.print_player_data(self.player)

    def print_win_rate(self):
        win_rate = self.player.match_history_manager.get_win_rate()
        self.print_stats.print_win_rate(self.player.summoner_name,win_rate,self.player.total_matches_wanted)

    def print_players_champion_masteries(self):
        masteries = self.player.mastery_manager.get_champion_name_to_champion_mastery().items()
        self.print_stats.print_players_champion_masteries(masteries)

    def print_all_masteries_in_live_match(self):
        masteries = self.player.live_match_manager.get_live_match_champion_masteries()
        self.print_stats.print_all_masteries_in_live_match(masteries)

    def print_champions_in_current_match(self):
        match_data = self.player.live_match_manager.get_champion_and_player_on_each_team_in_live_match()
        self.print_stats.print_champions_in_current_match(match_data)

    def print_live_player_champion(self):
        my_champion = self.player.live_match_manager.get_live_player_champion()
        self.print_stats.print_live_player_champion(my_champion)

    def print_side_bans(self):
        bans = self.player.live_match_manager.get_side_bans()
        self.print_stats.print_side_bans(bans)

    def print_win_rate_per_champion(self):
        champion_win_rates = self.player.champions_stats_manager.calculate_win_rate_per_champion()
        self.print_stats.print_win_rate_per_champion(self.player.summoner_name, self.player.total_matches_wanted, champion_win_rates)

    def print_average_kda_per_champion(self):
        kdas = self.player.champions_stats_manager.get_average_kda_per_champion()
        self.print_stats.print_average_kda_per_champion(self.player.summoner_name,self.player.total_matches_wanted,kdas)

    def print_winrate_with_allies(self):
        ally_stats = self.player.lobby_manager.get_stats_with_allies()
        self.print_stats.print_win_rate_with_certain_teammates(ally_stats)

    def print_winrate_of_enemies_against_player(self):
        enemy_stats = self.player.lobby_manager.get_stats_of_enemies_against_player()
        self.print_stats.print_win_rate_of_enemies_against_player(enemy_stats)

    def print_win_rate_with_all_ally_champions(self):
        ally_champ_stats = self.player.lobby_manager.determine_win_rate_with_all_ally_champions()
        self.print_stats.print_win_rate_with_all_ally_champions(ally_champ_stats,self.player.total_matches_wanted)

    def print_win_rate_of_enemy_champions_against_player(self):
        enemy_champ_stats = self.player.lobby_manager.determine_win_rate_of_enemy_champions_against_player()
        self.print_stats.print_win_rate_of_enemy_champions_against_player(enemy_champ_stats,self.player.total_matches_wanted)

    def print_win_rate_of_player_against_enemy_champion(self):
        enemy_champ_stats = self.player.lobby_manager.determine_win_rate_of_enemy_champions_against_player()
        self.print_stats.print_win_rate_of_player_against_enemy_champion(enemy_champ_stats,self.player.total_matches_wanted)