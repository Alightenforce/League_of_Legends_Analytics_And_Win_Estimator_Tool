import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from Player import Player
from Print_Player_Stats import Print_Player_Stats
from Print_Stats import Print_Stats
import time

class Summoner_Input_Form(ttk.Frame):
    def __init__(self, parent, on_player_submit):
        super().__init__(parent)
        self.on_player_submit = on_player_submit  # This is the parents function so whenever self.on_player_submit is called, the parent function handle_player_loaded will be called (callback function)
        self.total_matches_wanted_entry = None
        self.region_entry = None
        self.tag_entry = None
        self.name_entry = None
        self.output_label = None

        self.create_summoner_input_information()

    def create_summoner_input_information(self):
        self.output_label = ttk.Label(self, text="", font=("",15))
        font_size = ("Arial", 15)
        name_label = ttk.Label(self, text="Summoner Name", padding=(10,0), font=font_size)
        self.name_entry = ttk.Entry(self, width=40, font=font_size)
        tag_label = ttk.Label(self, text="Summoner Tag", padding=(10,0), font=font_size)
        self.tag_entry = ttk.Entry(self, width=40, font=font_size)
        region_label = ttk.Label(self, text="Region Name", padding=(10,0), font=font_size)
        self.region_entry = ttk.Entry(self, width=40, font=font_size)
        total_matches_wanted_label = ttk.Label(self, text="Total Matches Wanted", padding=(10,0), font=font_size)
        self.total_matches_wanted_entry = ttk.Entry(self, width=40, font=font_size)
        name_label.grid(row=0, column=0)
        self.name_entry.grid(row=0, column=1)
        tag_label.grid(row=1, column=0)
        self.tag_entry.grid(row=1, column=1)
        region_label.grid(row=2, column=0)
        self.region_entry.grid(row=2, column=1)
        total_matches_wanted_label.grid(row=3, column=0)
        self.total_matches_wanted_entry.grid(row=3, column=1)
        button = ttk.Button(
            self,
            text="Run",
            command=self.process_summoner_information
        )
        button.grid(row=5, column=0, columnspan=2, pady = 20)
        self.output_label.grid(row=6, column=0, columnspan=2, pady = 5)


    def process_summoner_information(self):
        summoner_name = self.name_entry.get()
        summoner_tag = self.tag_entry.get()
        region = self.region_entry.get()
        total_matches_wanted = int(self.total_matches_wanted_entry.get())
        try:
            current_player = Player(
                summoner_name,
                summoner_tag,
                region,
                total_matches_wanted,
            )
            self.on_player_submit(current_player)
            self.output_label.config(text=f"Success: Loaded {summoner_name}#{summoner_tag} ({total_matches_wanted} matches)")
        except:
            self.output_label.config(text="Cannot find player!")

class Summoner_Stats(ttk.Frame):
    def __init__(self, parent, player):
        super().__init__(parent)
        self.player = player
        self.combobox = None
        self.output_text = None
        self.stat_selection()

    def stat_selection(self):
        label = ttk.Label(self, text="Stats Selection", font = ("Arial", 10))
        stat_options = [
            "Player Overview / Account Data",
            "Overall Win Rate",
            "Champion Masteries",
            "Live Match: All Players' Masteries",
            "Live Match: Champions & Teams",
            "Live Match: Current Player Champion",
            "Live Match: Team Bans",
            "Win Rate per Champion",
            "Average KDA per Champion",
            "Win Rate with Specific Teammates",
            "Enemy Win Rate Against Player",
            "Win Rate with Ally Champions",
            "Enemy Champion Win Rate Against Player",
            "Player Win Rate Against Enemy Champions",
        ]
        self.combobox = ttk.Combobox(self, values=stat_options, state='readonly', width=50, height=30, font = ("Arial", 10))
        self.combobox.set("Player Overview / Account Data")
        button = (ttk.Button
            (
            self,
            text="Get Data",
            command=self.determine_stat_choice
            ))
        label.pack()
        self.combobox.pack(pady=(0,250))
        button.pack()

        self.output_text = scrolledtext.ScrolledText(
            self,
            wrap=tk.WORD,
            width=100,
            height=40,
        )
        self.output_text.pack(expand=True)
        self.output_text.config()

    def determine_stat_choice(self):
        choice = self.combobox.get()
        print(f"Selected: {choice} for player: {self.player}")

        if not self.player:
            self.set_output_text("Error: Player not loaded yet.")
            return

        match choice:
            case "Player Overview / Account Data":
                self.get_player_overview()
            case "Overall Win Rate":
                self.get_overall_winrate()
            case "Champion Masteries":
                self.get_champion_masteries()
            case "Live Match: All Players' Masteries":
                self.get_live_players_masteries()
            case "Live Match: Champions & Teams":
                self.get_live_champions_and_teams()
            case "Live Match: Current Player Champion":
                self.get_live_current_champion()
            case "Live Match: Team Bans":
                self.get_live_team_bans()
            case "Win Rate per Champion":
                self.get_winrate_per_champion()
            case "Average KDA per Champion":
                self.get_average_kda_per_champion()
            case "Win Rate with Specific Teammates":
                self.get_winrate_with_teammates()
            case "Enemy Win Rate Against Player":
                self.get_enemy_winrate_against_player()
            case "Win Rate with Ally Champions":
                self.get_winrate_with_ally_champions()
            case "Enemy Champion Win Rate Against Player":
                self.get_enemy_champion_winrate()
            case "Player Win Rate Against Enemy Champions":
                self.get_winrate_against_enemy_champions()
            case _:
                print(f"Handler for '{choice}' not implemented yet.")

    def set_output_text(self, text: str):
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, text)
        self.output_text.config(state=tk.DISABLED)
        self.output_text.yview_moveto(0.0)

    def get_player_overview(self):
        info_text = f"""
        Player:  {self.player.summoner_name} #{self.player.summoner_tag}
        Level:   {self.player.summoner_level}
        Region:  {self.player.region} ({self.player.region_code})
        PUUID:   {self.player.puuid}
        Icon ID: {self.player.pfp_id}
        Matches: {self.player.total_matches_wanted}
        Version: {self.player.version_number}
        """
        self.set_output_text(info_text)

    def get_overall_winrate(self):
        win_rate = self.player.match_history_manager.get_win_rate()
        info_text = f"""
        Player's Win Rate:
        {self.player.summoner_name}'s win rate is {win_rate}% over the past {self.player.total_matches_wanted} matches
        """
        self.set_output_text(info_text)

    def get_champion_masteries(self):
        masteries = (
            self.player.mastery_manager.get_champion_name_to_champion_mastery().items()
        )
        lines = ["All Player's Champion Masteries:"]
        for name, points in masteries:
            lines.append(f"• {name}: {points:,}")
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_live_players_masteries(self):
        team_to_puuid_to_stats = (
            self.player.live_match_manager.get_live_match_champion_masteries()
        )
        lines = []
        for team_key, team_label in [
            ("blue_team", "Blue Team"),
            ("red_team", "Red Team"),
        ]:
            lines.append(f"{team_label} Masteries:")
            players = team_to_puuid_to_stats.get(team_key, {})
            for puuid, stats in players.items():
                username = stats.get("username", "Unknown")
                champ_name = stats.get("champion_name", "Unknown")
                mastery = stats.get("mastery", 0)
                rank = stats.get("x_most_played", "?")
                lines.append(
                    f"  • {username} ({champ_name}): {mastery:,} pts (#{rank} most played)"
                )
            lines.append("")
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_live_champions_and_teams(self):
        players_in_current_game = (
            self.player.live_match_manager.get_champion_and_player_on_each_team_in_live_match()
        )
        lines = []
        for team, data_list in players_in_current_game.items():
            team_title = "Blue Team:" if team == "blue_team" else "Red Team:"
            lines.append(team_title)
            for puuid, data in data_list.items():
                lines.append(
                    f"  • {data.get('username')} | Champion: {data.get('champion_name')}"
                )
            lines.append("")
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_live_current_champion(self):
        my_champion = (
            self.player.live_match_manager.get_live_player_champion()
        )
        info_text = f"Player's Current Champion in Live Match:\n• {my_champion}"
        self.set_output_text(info_text)

    def get_live_team_bans(self):
        side_bans = self.player.live_match_manager.get_side_bans()
        lines = ["Blue Side Bans:"]
        for champion in side_bans.get("blue_side", []):
            lines.append(f"  • {champion}")
        lines.append("\nRed Side Bans:")
        for champion in side_bans.get("red_side", []):
            lines.append(f"  • {champion}")
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_winrate_per_champion(self):
        champion_win_rates = (
            self.player.champions_stats_manager.calculate_win_rate_per_champion()
        )
        lines = [
            f"{self.player.summoner_name}'s Win Rate per Champion (Last {self.player.total_matches_wanted} games):"
        ]
        for champion_name, data in champion_win_rates.items():
            lines.append(
                f"• {champion_name}: {data['Win_Rate']}% over {data['Total_Matches']} game(s)"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_average_kda_per_champion(self):
        kdas = (
            self.player.champions_stats_manager.get_average_kda_per_champion()
        )
        lines = [
            f"{self.player.summoner_name}'s Average KDA per Champion (Last {self.player.total_matches_wanted} games):"
        ]
        for champion_name, data in kdas.items():
            lines.append(
                f"• {champion_name}: {data['Avg_KDA']} KDA | {data['Avg_Kills']}/{data['Avg_Deaths']}/{data['Avg_Assists']}"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_winrate_with_teammates(self):
        ally_stats = self.player.lobby_manager.get_stats_with_allies()
        lines = ["Win Rate with Teammates:"]
        for name, stats in ally_stats.items():
            lines.append(
                f"• {name}: {stats['winrate']}% over {stats['total_matches']} match(es) ({stats['wins']}W, {stats['losses']}L)"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_enemy_winrate_against_player(self):
        enemy_stats = (
            self.player.lobby_manager.get_stats_of_enemies_against_player()
        )
        lines = ["Enemy Players' Win Rate Against You:"]
        for name, stats in enemy_stats.items():
            lines.append(
                f"• {name}: {stats['winrate']}% over {stats['total_matches']} match(es) ({stats['wins']}W, {stats['losses']}L)"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_winrate_with_ally_champions(self):
        ally_champ_stats = (
            self.player.lobby_manager.determine_win_rate_with_all_ally_champions()
        )
        lines = [
            f"Win Rate with Ally Champions (in {self.player.total_matches_wanted} matches):"
        ]
        for name, stats in ally_champ_stats.items():
            lines.append(
                f"• {name}: {stats['winrate']}% win rate ({stats['wins']}W, {stats['losses']}L) over {stats['total_matches']} matches"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_enemy_champion_winrate(self):
        enemy_champ_stats = (
            self.player.lobby_manager.determine_win_rate_of_enemy_champions_against_player()
        )
        lines = [
            f"Enemy Champions' Win Rate Against You (in {self.player.total_matches_wanted} matches):"
        ]
        for name, stats in enemy_champ_stats.items():
            lines.append(
                f"• {name}: {stats['winrate']}% win rate ({stats['wins']}W, {stats['losses']}L) over {stats['total_matches']} matches"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

    def get_winrate_against_enemy_champions(self):
        enemy_champ_stats = (
            self.player.lobby_manager.determine_win_rate_of_enemy_champions_against_player()
        )
        lines = [
            f"Your Win Rate Against Enemy Champions (in {self.player.total_matches_wanted} matches):"
        ]
        for name, stats in enemy_champ_stats.items():
            player_win_rate = round(100 - stats["winrate"], 2)
            lines.append(
                f"• {name}: {player_win_rate}% win rate ({stats['losses']}W, {stats['wins']}L) over {stats['total_matches']} matches"
            )
        info_text = "\n".join(lines)
        self.set_output_text(info_text)

class LolApp (tk.Tk):
    def __init__(self):
        super().__init__()
        self.current_player = None
        self.name_entry = None
        self.title("League of Legends Analytics Tool")
        self.geometry("1280x720")

        self.input_form = Summoner_Input_Form(self, on_player_submit=self.handle_player_loaded)
        self.input_form.pack(padx=20, pady=(40,0))

        self.stats = Summoner_Stats(self, self.current_player)
        self.stats.pack(padx=20, pady=20, fill="both")

    def handle_player_loaded(self, player):
        self.current_player = player
        self.stats.player = player


if __name__ == "__main__":
    app = LolApp()
    app.mainloop()