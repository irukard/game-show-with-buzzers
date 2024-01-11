import tkinter as tk
from tkinter import ttk, PhotoImage, Canvas
from ansi_color import Color
import pybuzzers
import time
import os
import sys
import winsound
import threading

# import pyautogui
# Use multimedia keys to control media player: pyautogui.press("nexttrack")
# Works with Spotify on Windows
# "playpause", "stop", "prevtrack", "nexttrack", "volumemute", etc

# Enable colors support in terminal
os.system("")

class Game(tk.Tk):
    def __init__(self, number_of_teams: int):
        super().__init__()
        
        self.we_got_buzz = False
        self.full_screen_enabled = False
        self.round_number = 1
        self.round_description = tk.StringVar(master=self)
        self.round_description.set(f"Round {self.round_number}")
        self.song_number = 1
        self.song_description = tk.StringVar(master=self)
        self.song_description.set(f"Song {self.round_number}")
        self.validate_number_of_teams(number_of_teams)
        self.teams = []
        
        # Game Master Control Panel window
        self.title("Name That Tune! Game Master Control Panel")
        self.geometry("1200x600")
        self.state("icon")
        self.frame_center = tk.Frame(master=self)
        self.frame_center.pack(side="top", pady=(50,50))
        self.label_gmcp_round_number = tk.Label(master=self.frame_center,
                                       font="Bahnschrift 36 bold",
                                       justify="center",
                                       textvariable=self.round_description)
        self.label_gmcp_round_number.pack(side="top")
        self.label_gmcp_song_number = tk.Label(master=self.frame_center,
                                      font="Bahnschrift 36 bold",
                                      justify="center",
                                      textvariable=self.song_description)
        self.label_gmcp_song_number.pack(side="top")
        
        self.frame_management = tk.Frame(master=self)
        self.button_next_turn = tk.Button(master=self.frame_management,
                                           text="▶ Try again",
                                           command=self.round_again,
                                           padx=7,
                                           pady=7)
        self.button_next_turn.pack(side="left", padx=15)
        self.button_next_turn = tk.Button(master=self.frame_management,
                                           text="⏩ Next round",
                                           command=self.next_round,
                                           padx=7,
                                           pady=7,
                                           background="red")
        self.button_next_turn.pack(side="left", padx=15)
        self.frame_management.pack(side="top")
        
        # Presentation window with fulscreen option
        self.presentation = tk.Toplevel(master = self)
        self.presentation.title("Name That Tune! (F11 to fullscreen)")
        self.presentation.geometry("1600x900")
        self.presentation.bind("<F11>", self.toggle_fullscreen)
        self.presentation.bind("<Escape>", self.exit_fullscreen)
        self.bg = PhotoImage(file = "./img/background.png")
        self.canvas = Canvas(self.presentation)
        self.canvas.pack(fill = "both", expand = True)
        self.canvas.create_image(0, 0, image = self.bg, anchor = "nw")
        self.label_round_number = tk.Label(master=self.presentation,
                                  font="Bahnschrift 75 bold",
                                  foreground="#ffffff",
                                  background="#7840e3",
                                  textvariable=self.round_description)
        self.canvas.create_window(350, 150, window=self.label_round_number, anchor="w")
        self.label_song_number = tk.Label(master=self.presentation,
                                 font="Bahnschrift 60 bold",
                                 foreground="#ebdc24",
                                 background="#7840e3",
                                 textvariable=self.song_description)
        self.canvas.create_window(350, 250, window=self.label_song_number, anchor="w")
        self.frame_center_presentation = tk.Frame(master=self.presentation,
                                     background="#7840e3")
        self.canvas.create_window(960, 350, window=self.frame_center_presentation, anchor="n")

        for i in range(number_of_teams):
            self.teams.append(Team(self, f"Team {chr(65+i)}"))
        
        self.buzzers_run_service()
    
    def toggle_fullscreen(self, event=None):
        if self.full_screen_enabled:
            self.exit_fullscreen()
        else:
            self.go_fullscreen()
    
    def go_fullscreen(self, event=None):
        self.full_screen_enabled = True
        self.old_geometry = self.presentation.geometry()
        self.presentation.overrideredirect(True)
        self.presentation.state("zoomed")

    def exit_fullscreen(self, event=None):
        self.full_screen_enabled = False
        self.presentation.state("normal")
        self.presentation.geometry(self.old_geometry)
        self.presentation.overrideredirect(False)
    
    def next_round(self):
        for team in self.teams:
            team.unlock_team()
        self.round_number += 1
        self.round_description.set(f"Round {self.round_number}")
        threading.Thread(target=self.buzzers_blink_active, args=[2]).start()
        self.we_got_buzz = False

    def round_again(self):
        for team in self.teams:
            if team.is_unlocked():
                team.unlock_team()
        threading.Thread(target=self.buzzers_blink_active, args=[2]).start()
        self.we_got_buzz = False

    def respond_to_buzz(self, _, id: int):
        if id < len(self.teams):
            if self.teams[id].is_unlocked() and (self.we_got_buzz == False):
                self.we_got_buzz = True
                winsound.PlaySound("./audio/sp-cheers.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
                self.teams[id].mark_team()
                self.controllers.set_light(id, True)

    def validate_number_of_teams(self, number_of_teams: int):
            if number_of_teams < 1:
                sys.exit(f"{Color.RED_HI}Error: You need at least one team to play{Color.RESET}")
            if number_of_teams > 4:
                sys.exit(f"{Color.RED_HI}Error: Sorry, but game only supports up to 4 players.{Color.RESET}")

    def buzzers_run_service(self):
        # Create instance
        try:
            self.controllers = pybuzzers.get_all_buzzers()[0]
        except IndexError:
            sys.exit(f"{Color.RED_HI}Error: No buzzers were detected{Color.RESET}\n"+
                     f"{Color.YELLOW_HI}Please connect receiver and run program again.{Color.RESET}")
        else:
            print(f"{Color.GREEN_HI}Buzzers detected{Color.RESET}")
            print("Please make sure that all buzzers blink.")
            self.buzzers_blink_all(2)
            self.buzzers_sweep_all(2)
        # Register callback
        self.controllers.on_buzz(self.respond_to_buzz)
        # Start buzzers listening service in another thread
        self.controllers.start_listening()

    def buzzers_blink_all(self, times:int):
        for _ in range(times):
            self.controllers.set_lights_on()
            time.sleep(0.2)
            self.controllers.set_lights_off()
            time.sleep(0.2)

    def buzzers_blink_active(self, times:int):
        lights_to_blink = []
        for team in self.teams:
            lights_to_blink.append(team.is_unlocked())
        for _ in range(times):
            self.controllers.set_lights(lights_to_blink)
            time.sleep(0.2)
            self.controllers.set_lights_off()
            time.sleep(0.2)

    def buzzers_sweep_all(self, times:int):
        for _ in range(times):
            for i in range(4):
                self.controllers.set_light(i, True)
                time.sleep(0.2)
                self.controllers.set_light(i, False)

class Team():
    def __init__(self, window: Game, team_name: str):
        self.team_score = tk.IntVar(master=window)
        self.team_name = tk.StringVar(master=window)
        self.team_name.set(team_name)
        self.team_locked = tk.BooleanVar(master=window)
        self.team_locked.set(False)

        # This frame will be displayed in the presentation window
        self.frame_team_presentation = tk.Frame(master=window.frame_center_presentation,
                                                background="#7840e3")
        self.label_team_name = tk.Label(master=self.frame_team_presentation,
                                        font="Bahnschrift 40 bold",
                                        foreground="#ffffff",
                                        background="#7840e3",
                                        justify="center",
                                        wraplength=350,
                                        height=2,
                                        width=12,
                                        anchor="s",
                                        textvariable=self.team_name)
        self.label_team_name.pack()
        self.label_team_score = tk.Label(master=self.frame_team_presentation,
                                         font="Bahnschrift 220 bold",
                                         foreground="#ffffff",
                                         background="#7840e3",
                                         justify="center",
                                         anchor="n",
                                         textvariable=self.team_score)
        self.label_team_score.pack()
        self.frame_team_presentation.pack(side="left")
        
        # This frame will be displayed in Game Master Control Panel
        self.frame_team_gmcp = tk.Frame(master=window.frame_center)
        
        self.frame_name_config = tk.Frame(master=self.frame_team_gmcp)
        self.field_team_name = tk.Entry(master = self.frame_name_config,
                                        textvariable = self.team_name,
                                        width=20,
                                        relief="flat",
                                        justify="center",
                                        borderwidth=10,
                                        background="#ffffff",
                                        font="Bahnschrift 14")
        self.field_team_name.pack()
        self.frame_name_config.pack(padx=20)
        
        self.frame_control = tk.Frame(master=self.frame_team_gmcp)

        self.button_rem = tk.Button(master=self.frame_control,
                                    text="➖",
                                    command=self.loose_point,
                                    background="red",
                                    padx=10,
                                    pady=10)
        self.button_rem.pack(side = "left", padx=5) 

        self.button_lock = tk.Button(master=self.frame_control,
                                text="Lock",
                                background="yellow",
                                command=self.lock_and_unlock,
                                padx=10,
                                pady=10,
                                width=6)
        self.button_lock.pack(side = "left", padx=5)

        self.button_add = tk.Button(master=self.frame_control,
                                    text="➕",
                                    background="green",
                                    command=self.add_point,
                                    padx=10,
                                    pady=10)
        self.button_add.pack(side = "left", padx=5)
        self.frame_control.pack(pady=20)
        
        self.frame_team_gmcp.pack(side="left")
        
    def add_point(self):
        self.team_score.set(self.team_score.get() + 1)
        
    def loose_point(self):
        if self.team_score.get() > 0:
            self.team_score.set(self.team_score.get() - 1)
    
    def lock_and_unlock(self):
        if self.team_locked.get():
            self.unlock_team()
        else:
            self.lock_team()
        
    def lock_team(self):
        self.label_team_name.configure(foreground="#5d31b0")
        self.label_team_score.configure(foreground="#5d31b0")
        self.button_lock.configure(text="Unlock")
        self.field_team_name.configure(background="#bdbdbd")
        self.team_locked.set(True)

    def unlock_team(self):
        self.label_team_name.configure(foreground="#ffffff")
        self.label_team_score.configure(foreground="#ffffff")
        self.field_team_name.configure(background="#ffffff")
        self.button_lock.configure(text="Lock")
        self.team_locked.set(False)

    def mark_team(self):
        self.label_team_name.configure(foreground="#ebdc24")
        self.label_team_score.configure(foreground="#ebdc24")

    def is_unlocked(self):
        if not self.team_locked.get():
            return True
        else:
            return False
    
def main():
    game = Game(4)
    game.mainloop()

if __name__ == "__main__":
    main()