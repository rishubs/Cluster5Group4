from pyo import *
from pynput import keyboard
import os
import time
import math

#make and start pyo server
s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

class Sound():
    '''stores a sound file/player, and is spatialized based on
    the user's coordinates'''
    def __init__(self, filename, coords, mul,user,loop=False):
        '''makes a sound located at coords in the plane'''
        self.x = coords[0]  #store the x coord of the sound
        self.y = coords[1]  #store the y coord
        self.user = user    #store the user (to use their coords later)
        self.sndPlayer = SfPlayer(filename,loop=loop,mul=mul)   #store sound as player
        self.hrtf = HRTF(self.sndPlayer)  #store hrtf
    def play(self):
        '''plays the sound, spatialized to user's initial coords'''
        userCoords = self.user.get_coords() #get user's initial coords
        userAngle = self.user.get_angle()   #get users initial angle 
        self.set_mul_and_azi(userCoords,userAngle)  #set the volume and angle of the sound initially
        self.hrtf.out()                             #and send it out
    def get_azi(self, userCoords,userAngle):
        '''returns the proper azimuth in order to spatialize the sound based on user's coords'''
        x1 = userCoords[0]  #get coords
        y1 = userCoords[1]
        dx = x1 - self.x    #calculate distance between sound and user on x and y axes
        dy = y1 - self.y
        angle = 0           #initialize angle (for scope reasons
        if dx != 0:         #only calculate if dx isnt zero (otherwise we get zero division error)
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
            self.turn(1)
        elif key == keyboard.Key.right:
            self.turn(-1)
        elif key == keyboard.Key.up:
            self.take_step(True)
        elif key == keyboard.Key.down:
            self.take_step(False)
        print(self.x, self.y, self.angle)
    def turn(self, dir):
        targetAngle = (self.angle + dir*90) % 360
        while round(self.angle) != round(targetAngle):
            self.angle += dir * 5
            self.angle = self.angle % 360
            time.sleep(0.1)
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
