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
            angle = ((math.atan2(dy,dx))*(180/math.pi) - 90 + userAngle)   #calculate azi (get arctan of the slope, then convert to degrees
            #then rotate 90 degrees to account for tan being based on west, not north, then account for user angle (which way they are facing)
        else:
            if dy < 0:  #if user is north of sound
                angle = 180 - userAngle #sound is behind them, - user angle
            else:
                angle = 0 - userAngle   #if user is south of sound, should be in front (taking into acount their angle)
        return angle
    def get_mul(self, userCoords):
        '''returns volume for the sound based on its distance from user'''
        x1 = userCoords[0]  #get coords
        y1 = userCoords[1]
        dx = self.x - x1    #calculate distance
        dy = self.y = y1
        distance = math.sqrt(dx**2+dy**2)   #use pythagoras
        if distance <=1:    #if user is within 1 unit
            return 1        #as loud as possible
        else:
            return 1/distance   #mul is inversely proportional to user's distance
    def set_mul_and_azi(self, userCoords, userAngle):
        '''sets the mul and azi in the hrtf based on user position/angle'''
        azi = float(self.get_azi(userCoords,userAngle))    #use function to get azi
        mul = float(self.get_mul(userCoords))              #use function to get mul
        self.hrtf.setAzimuth(azi)                   #set azi
        self.hrtf.setMul(mul)                       #set mul
    def is_playing(self):
        '''returns a bool based on whether the sound is still playing'''
        return self.hrtf.isPlaying()    #use hrtf built in method lol

class User():
    '''represents a user in the coordinate plane with a position and an angle
    controlled by arrow keys (up = forward, l/r = turn 90 degrees)'''
    def __init__(self, coords):
        '''creats a user with coordinates'''
        self.x = coords[0]
        self.y = coords[1]
        self.angle = 0  #start facing north
    def on_press(self, key):
        '''changes the user's position and angle based on keystrokes'''
        if key == keyboard.Key.left: 
            self.turn(1)    #turn positive angle (left), on left keystroke
        elif key == keyboard.Key.right:
            self.turn(-1)   #turn a negative angle (right), on right keystroke
        elif key == keyboard.Key.up:
            self.take_step(True)    #take a step forward
        elif key == keyboard.Key.down:  
            self.take_step(False)   #take a step back
        print(self.x, self.y, self.angle)   #print coords and angle
    def turn(self, dir):
        '''changes the user's angle slowly, 90 degrees left or right'''
        targetAngle = (self.angle + dir*90) % 360   #calculate target angle based on direction (1 or -1)
        while round(self.angle) != round(targetAngle):  #keep iterating until we iterate angle enough to get to the target
            self.angle += dir * 5              #add or subtract based on dir
            self.angle = self.angle % 360      #keep it mod 360
            time.sleep(0.1)                    #wait, so the turn happens gradually
    def take_step(self, forward):
        '''takes a step forward, in the direction the user is facing'''
        dir = 1             #make dir 1 or -1 based on the value of forward (bool)
        if not forward:
            dir = -1
        angleFromX = (90 + self.angle)*(math.pi/180)   #calculate the angle from the western x axis (bc trig)
        changeX = dir * math.cos(angleFromX)            #calculate steps to take in x and y direction
        changeY = dir * math.sin(angleFromX)
        self.x += changeX       #iterate coords accordingly
        self.y += changeY
    def get_coords(self):
        '''returns the player's coordinates'''
        return [self.x, self.y]
    def get_angle(self):
        '''returns the players angle'''
        return self.angle

user = User([0,0])  #make a user at 0,0
piano = Sound("./Sounds/piano_unaltered.wav", [-10,0], 0.5, user)   #make the sound at -10, 0

userCoords = User.get_coords()


def press(key):     #make the press function
    global user
    user.on_press(key)  #it just calls the user method

listener = keyboard.Listener(on_press=press)    #make and start listener
listener.start()
piano.play()    #start playing piano

while piano.is_playing():       #while its playing, constantly update the azi and mul based on user's coords and angle
    piano.set_mul_and_azi(user.get_coords(), user.get_angle())

time.sleep(60)  #idk why this is here but it works
