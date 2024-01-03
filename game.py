import pybuzzers
import time
import winsound
import pyautogui
# "playpause", "stop", "prevtrack", "nexttrack", "volumemute"

buzzer = pybuzzers.get_all_buzzers()[0]

def buzzers_blink(buzzer_set: pybuzzers.BuzzerSet, n:int):
    for _ in range(n):
        buzzer_set.set_lights_on()
        time.sleep(0.25)
        buzzer_set.set_lights_off()
        time.sleep(0.25)

def buzzers_sweep(buzzer_set: pybuzzers.BuzzerSet, n:int):
    for _ in range(n):
        for i in range(4):
            buzzer_set.set_light(i, True)
            time.sleep(0.1)
            buzzer_set.set_light(i, False)

def buzzers_test_lights(buzzer_set: pybuzzers.BuzzerSet):
    buzzers_blink(buzzer_set, 2)
    buzzers_sweep(buzzer_set, 2)
    
def audio_play_bell():
    winsound.PlaySound("./audio/sp-cheers.wav", winsound.SND_FILENAME | winsound.SND_ASYNC)
    
# Define an event handler we want to run every time a button is pressed
def respond_to_press(buzzer_set: pybuzzers.BuzzerSet, buzzer: int, button: int):
    match button:
        case 0:
            audio_play_bell()
            pyautogui.press("playpause")
        case 1:
            pyautogui.press("nexttrack")
        case 2:
            pyautogui.press("prevtrack")
        case 3:
            pyautogui.press("stop")
        case 4:
            pyautogui.press("volumemute")
        
    button_colour = pybuzzers.COLOUR[button]
    print(f"{button_colour} button pressed on buzzer {buzzer}!")
    buzzer_set.set_light(buzzer, True)

buzzers_test_lights(buzzer)

buzzer.on_button_down(respond_to_press)
buzzer.start_listening()

#buzzer.on_buzz()

