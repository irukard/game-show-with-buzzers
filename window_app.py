import tkinter as tk
from tkinter import ttk
from ansi_color import Color
import pybuzzers
import time
import os

# import winsound
# Play wav file under windows
# winsound.PlaySound("./audio/audio_clip.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)

# import pyautogui
# Use multimedia keys to control media player: pyautogui.press("nexttrack")
# "playpause", "stop", "prevtrack", "nexttrack", "volumemute", etc

os.system("") # enable colors

class Game(tk.Tk):
    def __init__(self, number_of_teams: int):
        super().__init__()
        self.title("Name That Tune!")
        self.geometry("1600x900")
        self.frame_center = ttk.Frame(master=self)
        self.frame_center.pack(side="top", pady=(200,100))
        self.teams:Team = []
        self.we_got_buzz = False

        self.controlers = GameBuzzers()
        self.controlers.buzzer_set.on_buzz(self.respond_to_buzz)
        self.controlers.buzzer_set.start_listening()
        
        for i in range(number_of_teams):
            self.teams.append(Team(self, "Team " + str(i+1)))

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
        self.controlers.buzzers_blink(2)
        self.we_got_buzz = False

    def round_again(self):
        for team in self.teams:
            if team.is_unlocked():
                team.unlock_team()
        self.controlers.buzzers_blink(2)
        self.we_got_buzz = False

    def respond_to_buzz(self, _, id: int):
        if self.teams[id].is_unlocked() and (self.we_got_buzz == False):
            self.we_got_buzz = True
            self.teams[id].mark_team()
            self.controlers.buzzer_set.set_light(id, True)

class Team():
    def __init__(self, window: Game, team_name: str):
        self.team_score = tk.IntVar()
        self.team_name = tk.StringVar()
        self.team_name.set(team_name)
        self.team_locked = tk.BooleanVar()
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

class GameBuzzers():
    def __init__(self):
        try:
            self.buzzer_set = pybuzzers.get_all_buzzers()[0]
        except IndexError:
            print(f"{Color.RED_HI}Error: No buzzers were detected{Color.RESET}")
            print("Please connect receiver and run program again.")
            quit()
        else:
            print(f"{Color.GREEN_HI}Buzzers detected{Color.RESET}")
            self.buzzers_blink(2)
            self.buzzers_sweep(2)

    def buzzers_blink(self, times:int):
        for _ in range(times):
            self.buzzer_set.set_lights_on()
            time.sleep(0.2)
            self.buzzer_set.set_lights_off()
            time.sleep(0.2)

    def buzzers_sweep(self, times:int):
        for _ in range(times):
            for i in range(4):
                self.buzzer_set.set_light(i, True)
                time.sleep(0.1)
                self.buzzer_set.set_light(i, False)
    
def main():
    game = Game(4)
    game.mainloop()

if __name__ == "__main__":
    main()