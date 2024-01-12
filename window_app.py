import tkinter as tk
from tkinter import ttk, PhotoImage, Canvas
from ansi_color import Color
import pybuzzers
import time
import os
import sys
import winsound
import threading

#from lang.en import Lang
from lang.pl import Lang

# import pyautogui
# Use multimedia keys to control media player: pyautogui.press("nexttrack")
# Works with Spotify on Windows
# "playpause", "stop", "prevtrack", "nexttrack", "volumemute", etc

# Enable colors support in terminal
os.system("")

# Nice colors:
#red    #ff595e
#yellow #ffca3a
#green  #8ac926
#blue   #1982c4
#violet #6a4c93

class Game(tk.Tk):
    def __init__(self, number_of_teams: int):
        super().__init__()
        
        self.we_got_buzz = False
        self.full_screen_enabled = False
        self.round_number = 1
        self.round_description = tk.StringVar(master=self)
        self.round_description.set(f"{Lang.ROUND} {self.round_number}")
        self.song_number = 1
        self.song_description = tk.StringVar(master=self)
        self.song_description.set(f"{Lang.SONG} {self.round_number}")
        self.validate_number_of_teams(number_of_teams)
        self.teams = []
        
        # Game Master Control Panel window
        self.title(Lang.GMCP_WINDOW_TITLE)
        self.geometry("1280x720")
        self.frame_center = tk.Frame(master=self)

        self.frame_gmcp_round_and_song_management = tk.Frame(master=self)
        # round
        self.frame_gmcp_round_management = tk.Frame(master=self.frame_gmcp_round_and_song_management)
        self.label_gmcp_round_number = tk.Label(master=self.frame_gmcp_round_management,
                                                font="Bahnschrift 32 bold",
                                                justify="center",
                                                textvariable=self.round_description,
                                                width=10,
                                                padx=10,
                                                pady=5)
        self.label_gmcp_round_number.pack(side="left")
        self.button_prev_round = tk.Button(master=self.frame_gmcp_round_management,
                                          text=Lang.GMCP_BUTTON_PREV_ROUND,
                                          command=lambda: self.change_round(-1),
                                          font="Bahnschrift 12 bold",
                                          background="#ff595e", # red
                                          relief="flat",
                                          padx=0,
                                          pady=20,
                                          width=20)
        self.button_prev_round.pack(side="left")
        self.button_next_round = tk.Button(master=self.frame_gmcp_round_management,
                                           text=Lang.GMCP_BUTTON_NEXT_ROUND,
                                           command=lambda: self.change_round(+1),
                                           font="Bahnschrift 12 bold",
                                           background="#8ac926", # green
                                           relief="flat",
                                           padx=0,
                                           pady=20,
                                           width=20)
        self.button_next_round.pack(side="left")
        self.frame_gmcp_round_management.pack(anchor="w", pady=20)

        # song
        self.frame_gmcp_song_management = tk.Frame(master=self.frame_gmcp_round_and_song_management)
        self.label_gmcp_song_number = tk.Label(master=self.frame_gmcp_song_management,
                                      font="Bahnschrift 32 bold",
                                      justify="center",
                                      textvariable=self.song_description,
                                      width=10,
                                      padx=10,
                                      pady=5)
        self.label_gmcp_song_number.pack(side="left")
        self.button_prev_song = tk.Button(master=self.frame_gmcp_song_management,
                                           text=Lang.GMCP_BUTTON_PREV_SONG,
                                           command=lambda: self.change_song(-1),
                                           font="Bahnschrift 12 bold",
                                           background="#ff595e", # red
                                           relief="flat",
                                           padx=0,
                                           pady=20,
                                           width=20)
        self.button_prev_song.pack(side="left")
        self.button_try_again = tk.Button(master=self.frame_gmcp_song_management,
                                          text=Lang.GMCP_BUTTON_TRY_AGAIN,
                                          command=self.song_again,
                                          font="Bahnschrift 12 bold",
                                          background="#ffca3a", # yellow
                                          relief="flat",
                                          padx=0,
                                          pady=20,
                                          width=20)
        self.button_try_again.pack(side="left")
        self.button_next_song = tk.Button(master=self.frame_gmcp_song_management,
                                           text=Lang.GMCP_BUTTON_NEXT_SONG,
                                           command=lambda: self.change_song(+1),
                                           font="Bahnschrift 12 bold",
                                           background="#8ac926", # green
                                           relief="flat",
                                           padx=0,
                                           pady=20,
                                           width=20)
        self.button_next_song.pack(side="left")
        self.frame_gmcp_song_management.pack(anchor="w", pady=20)
        
        self.frame_gmcp_round_and_song_management.pack(side="top")

        self.frame_center.pack(side="top", pady=(50,50))

        self.frame_gmcp_end_game = tk.Frame(master=self)
        self.button_end_game = tk.Button(master=self.frame_gmcp_end_game,
                                         text=Lang.GMCP_BUTTON_END_GAME,
                                         command=self.end_game,
                                         font="Bahnschrift 12 bold",
                                         background="#6a4c93", # violet
                                         foreground="#ffffff",
                                         relief="flat",
                                         padx=0,
                                         pady=20,
                                         width=20)
        self.button_end_game.pack(side="left")
        self.frame_gmcp_end_game.pack(side="bottom", pady=20)
        
        # Presentation window with fulscreen option
        self.presentation = tk.Toplevel(master = self)
        self.presentation.title(Lang.PRESENTATION_WINDOW_TITLE)
        self.presentation.geometry("1600x900")
        self.presentation.bind("<F11>", self.toggle_fullscreen)
        self.presentation.bind("<Escape>", self.exit_fullscreen)
        self.canvas = Canvas(self.presentation, bg="#7840e3")
        self.canvas.pack(fill = "both", expand = True)
        if os.path.isfile("./img/background.png"):
            self.bg = PhotoImage(file = "./img/background.png")
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
        self.canvas.create_window(350, 260, window=self.label_song_number, anchor="w")
        self.frame_center_presentation = tk.Frame(master=self.presentation,
                                     background="#7840e3")
        self.canvas.create_window(960, 350, window=self.frame_center_presentation, anchor="n")

        for i in range(number_of_teams):
            self.teams.append(Team(self, f"{Lang.TEAM} {chr(65+i)}"))
        
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

    def change_round(self, number: int):
        for team in self.teams:
            team.unlock_team()
        if self.round_number + number < 1:
            self.round_number = 1
        else:
            self.round_number += number
        self.round_description.set(f"{Lang.ROUND} {self.round_number}")
        self.song_number = 1
        self.song_description.set(f"{Lang.SONG} {self.song_number}")
        threading.Thread(target=self.buzzers_blink_active, args=[2]).start()
        self.we_got_buzz = False

    def change_song(self, number: int):
        for team in self.teams:
            team.unlock_team()
        if self.song_number + number < 1:
            self.song_number = 1
        else:
            self.song_number += number
        self.song_description.set(f"{Lang.SONG} {self.song_number}")
        threading.Thread(target=self.buzzers_blink_active, args=[2]).start()
        self.we_got_buzz = False

    def song_again(self):
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
                sys.exit(f"{Color.RED_HI}{Lang.ERROR_NOT_ENOUGH_PLAYERS}{Color.RESET}")
            if number_of_teams > 4:
                sys.exit(f"{Color.RED_HI}{Lang.ERROR_TOO_MANY_PLAYERS}{Color.RESET}")

    def buzzers_run_service(self):
        # Create instance
        try:
            self.controllers = pybuzzers.get_all_buzzers()[0]
        except IndexError:
            sys.exit(f"{Color.RED_HI}{Lang.ERROR_BUZZERS_NOT_DETECTED}{Color.RESET}\n"+
                     f"{Color.YELLOW_HI}{Lang.ERROR_BUZZERS_NOT_DETECTED_HINT}{Color.RESET}")
        else:
            print(f"{Color.GREEN_HI}{Lang.SUCCESS_BUZZERS_DETECTED}{Color.RESET}")
            print(f"{Color.YELLOW_HI}{Lang.SUCCESS_BUZZERS_DETECTED_HINT}{Color.RESET}")
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

    def end_game(self):
        self.round_description.set(Lang.WINNER)
        self.song_description.set("")
        scores = []
        for team in self.teams:
            scores.append(team.team_score.get())
        for team in self.teams:
            if team.team_score.get() == max(scores):
                team.mark_team()
            else:
                team.lock_team()

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
        self.frame_gmcp_team = tk.Frame(master=window.frame_center)
        self.frame_gmcp_name = tk.Frame(master=self.frame_gmcp_team)
        self.field_team_name = tk.Entry(master = self.frame_gmcp_name,
                                        textvariable = self.team_name,
                                        width=20,
                                        relief="flat",
                                        justify="center",
                                        borderwidth=10,
                                        background="#ffffff",
                                        font="Bahnschrift 14")
        self.field_team_name.pack()
        self.frame_gmcp_name.pack(padx=20, pady=10)
        
        self.frame_gmcp_score_control = tk.Frame(master=self.frame_gmcp_team)
        self.button_rem = tk.Button(master=self.frame_gmcp_score_control,
                                    text="➖",
                                    command=self.loose_point,
                                    background="#ff595e", # red
                                    relief="flat",
                                    padx=10,
                                    pady=10)
        self.button_rem.pack(side = "left", padx=5) 
        self.label_gmcp_team_score = tk.Label(master=self.frame_gmcp_score_control,
                                              font="Bahnschrift 32 bold",
                                              justify="center",
                                              width=2,
                                              textvariable=self.team_score)
        self.label_gmcp_team_score.pack(side = "left", padx=5)
        self.button_add = tk.Button(master=self.frame_gmcp_score_control,
                                    text="➕",
                                    background="#8ac926", # green
                                    relief="flat",
                                    command=self.add_point,
                                    padx=10,
                                    pady=10)
        self.button_add.pack(side = "left", padx=5)
        self.frame_gmcp_score_control.pack(padx=20, pady=10)
        
        self.frame_gmcp_lock_control = tk.Frame(master=self.frame_gmcp_team)
        self.button_lock = tk.Button(master=self.frame_gmcp_lock_control,
                                     text=Lang.GMCP_BUTTON_LOCK,
                                     background="#ffca3a", # yellow
                                     relief="flat",
                                     command=self.lock_and_unlock,
                                     padx=10,
                                     pady=10,
                                     width=8)
        self.button_lock.pack()
        self.frame_gmcp_lock_control.pack(padx=20, pady=10)

        self.frame_gmcp_team.pack(side="left")
        
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
        self.button_lock.configure(text=Lang.GMCP_BUTTON_UNLOCK)
        self.field_team_name.configure(background="#bdbdbd")
        self.team_locked.set(True)

    def unlock_team(self):
        self.label_team_name.configure(foreground="#ffffff")
        self.label_team_score.configure(foreground="#ffffff")
        self.field_team_name.configure(background="#ffffff")
        self.button_lock.configure(text=Lang.GMCP_BUTTON_LOCK)
        self.team_locked.set(False)

    def mark_team(self):
        self.label_team_name.configure(foreground="#ebdc24")
        self.label_team_score.configure(foreground="#ebdc24")
        self.field_team_name.configure(background="orange")

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