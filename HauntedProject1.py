from pyo import *
from pynput import keyboard
import os
import time

s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

path = os.path.dirname(__file__)
snd_path = path + "/Jul16_actualFootsteps.wav"
soundplayer = SfPlayer(snd_path, loop=True, mul=0.3)
v = HRTF(soundplayer, azimuth=0, elevation=0, mul=0.5)

# Function runs when a key is pressed
def on_press(key):
    global v
    try:
        print("alphanumeric key {0} pressed".format(key.char))
    except:
        print('special key {0} pressed'.format(key))
        # If user clicks the "up" arrow, sound starts playing
        if key == keyboard.Key.up:
            v.out()

# Listening for a key press
listener = keyboard.Listener(
    on_press=on_press)

listener.start()

time.sleep(60)