from pyo import *
from pynput import keyboard
import os
import time
import math

s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

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
        userAngle = self.user.get_angle()
        self.set_mul_and_azi(userCoords,userAngle)
        self.hrtf.out()
    def get_azi(self, userCoords,userAngle):
        x1 = userCoords[0]
        y1 = userCoords[1]
        dx = x1 - self.x
        dy = y1 - self.y
        angle = 0
        if dx != 0:
            angle = ((math.atan2(dy,dx))*(180/math.pi) - 90 + userAngle)
        else:
            if dy < 0:
                angle = 180 - userAngle
            else:
                angle = 0 - userAngle
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
    def set_mul_and_azi(self, userCoords, userAngle):
        azi = float(self.get_azi(userCoords,userAngle))
        mul = float(self.get_mul(userCoords))
        self.hrtf.setAzimuth(azi)
        self.hrtf.setMul(mul)
    def is_playing(self):
        return self.hrtf.isPlaying()

class User():
    def __init__(self, coords):
        self.x = coords[0]
        self.y = coords[1]
        self.angle = 0
    def on_press(self, key):
        if key == keyboard.Key.left:
            self.angle += 5
            self.angle = self.angle % 360
        elif key == keyboard.Key.right:
            self.angle -= 5
            self.angle = self.angle % 360
        elif key == keyboard.Key.up:
            self.take_step(True)
        elif key == keyboard.Key.down:
            self.take_step(False)
        print(self.x, self.y, self.angle)
    def take_step(self, forward):
        dir = 1
        if not forward:
            dir = -1
        angleFromX = (90 + self.angle)*(math.pi/180)
        changeX = dir * math.cos(angleFromX)
        changeY = dir * math.sin(angleFromX)
        self.x += changeX
        self.y += changeY
    def get_coords(self):
        return [self.x, self.y]
    def get_angle(self):
        return self.angle

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
    piano.set_mul_and_azi(user.get_coords(), user.get_angle())

time.sleep(60)
