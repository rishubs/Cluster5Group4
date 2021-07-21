from pyo import *
from pynput import keyboard
import os
import time
import math

s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()


userCoords = [0,0]
class Sound():
    """is a sound rawr"""
    def __init__(self, filename, coords, mul,user,loop=False):
        '''makes a sound located at coords'''
        self.x = coords[0]
        self.y = coords[1]
        self.user = user
        self.sndPlayer = SfPlayer(filename,loop=loop,mul=mul)
        self.hrtf = HRTF(self.sndPlayer)
    def play(self):
        userCoords = self.user.get_coords()
        self.set_mul_and_azi(userCoords)
        self.hrtf.out()
    def get_azi(self, userCoords):
        x1 = userCoords[0]
        y1 = userCoords[1]
        dx = self.x - x1
        dy = self.y = y1
        angle = 0
        if dx != 0:
            angle = (math.atan2(dy,dx))*(180/math.pi) - 90
        else:
            if dy < 0:
                angle = 180
        return angle
    def get_mul(self, userCoords):
        x1 = userCoords[0]
        y1 = userCoords[1]
        dx = self.x - x1
        dy = self.y = y1
        distance = math.sqrt(dx**2+dy**2)
        if distance <=1:
            return 1
        else:
            return 1/distance
    def set_mul_and_azi(self, userCoords):
        azi = float(self.get_azi(userCoords))
        mul = float(self.get_mul(userCoords))
        self.hrtf.setAzimuth(azi)
        self.hrtf.setMul(mul)
    def is_playing(self):
        return self.hrtf.isPlaying()

class User():
    def __init__(self, coords):
        self.x = coords[0]
        self.y = coords[1]
    def on_press(self, key):
        if key == keyboard.Key.left:
            self.x -= 1
        elif key == keyboard.Key.right:
            self.x += 1
        elif key == keyboard.Key.up:
            self.y += 1
        elif key == keyboard.Key.down:
            self.y -= 1
        print(self.x, self.y)
    def get_coords(self):
        return [self.x, self.y]

user = User([0,0])
piano = Sound("piano_unaltered.wav", [-10,0], 0.5, user)

'''
#SNDS_PATH = "hello.wav"
white_noise = Noise(0.3)
#sound_player = SfPlayer(SNDS_PATH, loop=True,  mul=0.3)
v = HRTF(white_noise, azimuth=0, elevation=0, mul=0.5).out()

def on_press(key):
    try:
        f = 'alphanumeric key {0} pressed'.format(key.char)
    except AttributeError:
        if key == keyboard.Key.left:

        elif key == keyboard.Key.right:
            azi += 10
            print(azi) # check what azi value is to make sure azi is changing
        v.setAzimuth(float(azi))
'''


# azi = Phasor(0.2, mul=360)

# listener = keyboard.Listener(
#     on_press=lambda event: on_press(event, azi=azi))
# print(azi)
# v = HRTF(sound_player, azimuth=azi, elevation=ele, mul=0.5)

def press(key):
    global user
    user.on_press(key)

listener = keyboard.Listener(on_press=press)
listener.start()
piano.play()
while piano.is_playing():
    piano.set_mul_and_azi(user.get_coords())

time.sleep(60)
