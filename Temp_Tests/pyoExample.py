from pyo import *
from pynput import keyboard
import time

s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

counter = 0

SNDS_PATH = "../Sounds/channels.wav"
white_noise = Noise(0.3)
sound_player = SfPlayer(SNDS_PATH, loop=True,  mul=0.3)
v = HRTF(white_noise, azimuth=0, elevation=0, mul=0.5).out()
c = HRTF(sound_player, azimuth=0, elevation=0, mul=0.5)

def on_press(key):
    global v
    global c
    global counter
    channelsToggle = False
    try:
        print('alphanumeric key {0} pressed'.format(key.char))
    except AttributeError:
        print('special key {0} pressed'.format(key))
        azi = v.azimuth
        # volume of white noise
        vol = v.mul
        # volume of sound_player
        cvol = c.mul
        if key == keyboard.Key.left:
            # subtract 10 from azi to move sound to the left
            azi -= 10
            # check what azi value is to make sure azi is changing
            print(azi)

        elif key == keyboard.Key.right:
            # subtract 10 from azi to move sound to the right
            azi += 10
            # check what azi value is to make sure azi is changing
            print(azi)
        elif key == keyboard.Key.up:
            # lower the volume of v when going forward
            if round(vol, 1) != 0.0:
                vol -= 0.1
            counter += 1
        # after going forward 3+ steps, start playing the "c" file
        if counter > 3 and channelsToggle == False:
            c.out()
            channelsToggle = True
        # change azi and vol values
        v.setAzimuth(float(azi))
        c.setAzimuth(float(azi))
        v.setMul(float(vol))



# azi = Phasor(0.2, mul=360)

# listener = keyboard.Listener(
#     on_press=lambda event: on_press(event, azi=azi))
# print(azi)
# v = HRTF(sound_player, azimuth=azi, elevation=ele, mul=0.5)


listener = keyboard.Listener(
    on_press=on_press)

listener.start()

time.sleep(60)