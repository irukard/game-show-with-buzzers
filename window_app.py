import tkinter as tk
from tkinter import ttk
from ansi_color import Color
import pybuzzers
import time
import os
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
        self.title("Name That Tune!")
        self.geometry("1600x900")
        self.frame_center = ttk.Frame(master=self)
        self.frame_center.pack(side="top", pady=(150,100))
        self.we_got_buzz = False
        self.round_number = 1
        self.round_title = tk.StringVar(master=self)
        self.round_title.set(f"Round {self.round_number}")

        self.label_round_number = ttk.Label(master=self.frame_center,
                                  font="Bahnschrift 72 bold",
                                  justify="center",
                                  textvariable=self.round_title)
        self.label_round_number.pack(side="top", pady=(0,50))
        
        self.validate_number_of_teams(number_of_teams)
        self.teams = []
        for i in range(number_of_teams):
            self.teams.append(Team(self, "Team " + str(i+1)))
        self.buzzers_run_service()

        # Frame with game management controls
        self.frame_management = ttk.Frame(master=self)
        self.button_next_turn = ttk.Button(master=self.frame_management,
                                           text="▶ Try again",
                                           command=self.round_again,
                                           padding=7)
        self.button_next_turn.pack(side="left", padx=15)
        self.button_next_turn = ttk.Button(master=self.frame_management,
                                           text="⏩ Next round",
                                           command=self.next_round,
                                           padding=7)
        self.button_next_turn.pack(side="left", padx=15)
        self.frame_management.pack(side="top")
    
    def next_round(self):
        for team in self.teams:
            team.unlock_team()
        self.round_number += 1
        self.round_title.set(f"Round {self.round_number}")
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
                print(f"{Color.RED_HI}Error: You need at least one team to play{Color.RESET}")
                quit()
            if number_of_teams > 4:
                print(f"{Color.RED_HI}Error: Sorry, but game only supports up to 4 players.{Color.RESET}")
                quit()

    def buzzers_run_service(self):
        # Create instance
        try:
            self.controllers = pybuzzers.get_all_buzzers()[0]
        except IndexError:
            print(f"{Color.RED_HI}Error: No buzzers were detected{Color.RESET}")
            print("Please connect receiver and run program again.")
            quit()
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
        
        self.frame_team = ttk.Frame(master=window.frame_center)
        
        self.label_team_name = ttk.Label(master=self.frame_team,
                                    font="Bahnschrift 40 bold",
                                    justify="center",
                                    wraplength=380,
                                    textvariable=self.team_name)
        self.label_team_name.pack()
        self.label_team_score = ttk.Label(master=self.frame_team,
                                     font="Bahnschrift 140 bold",
                                     justify="center",
                                     textvariable=self.team_score)
        self.label_team_score.pack()
        
        self.frame_control = ttk.Frame(master=self.frame_team)
        self.button_add = ttk.Button(master=self.frame_control,
                                text="➕",
                                command=self.add_point,
                                padding=7)
        self.button_add.pack(side = "right", padx=15)
        self.button_rem = ttk.Button(master=self.frame_control,
                                text="➖",
                                command=self.loose_point,
                                padding=7)
        self.button_rem.pack(side = "left", padx=15) 
        self.button_lock = ttk.Button(master=self.frame_control,
                                text="Lock",
                                command=self.lock_and_unlock,
                                padding=7)
        self.button_lock.pack(side = "top")
       
        self.frame_control.pack(pady=20)
        self.frame_config = ttk.Frame(master=self.frame_team)
        self.field_team_name = ttk.Entry(master = self.frame_config,
                                    textvariable = self.team_name,
                                    width=32,
                                    justify="center",
                                    font="Bahnschrift 10")
        self.field_team_name.pack()
        self.frame_config.pack(padx=80)
        self.frame_team.pack(side="left")
        
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
        self.label_team_name.configure(foreground="lightgray")
        self.label_team_score.configure(foreground="lightgray")
        self.button_lock.configure(text="Unlock")
        self.team_locked.set(True)

    def unlock_team(self):
        self.label_team_name.configure(foreground="black")
        self.label_team_score.configure(foreground="black")
        self.button_lock.configure(text="Lock")
        self.team_locked.set(False)

    def mark_team(self):
        self.label_team_name.configure(foreground="orange")
        self.label_team_score.configure(foreground="orange")

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