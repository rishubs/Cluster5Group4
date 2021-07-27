from pyo import *
from pynput import keyboard
import os
import time
import math
import turtle

#make and start pyo server
s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

class Sound():
    '''stores a sound file/player, and is spatialized based on
    the user's coordinates'''
    def __init__(self, filename, coords, mul,user, volRange, room, loop=False, triggered = False):
        '''makes a sound located at coords in the plane'''
        self.rooms = {'entry':[12,16,6,8],'music':[8,12,4,8],'family':[3,8,1,7],'kitchen':[0,6,7,12], \
                      'elevator':[6,8,8,12],'dining':[8,13,8,12],'bath':[],'master':[],'study':[],\
                      'library':[],'balcony':[]}
        self.roomCoords = self.rooms[room]
        self.x = coords[0]  #store the x coord of the sound
        self.y = coords[1]  #store the y coord
        self.user = user    #store the user (to use their coords later)
        self.volRange = volRange
        self.triggered = triggered
        self.played = False
        self.sndPlayer = SfPlayer(filename,loop=loop,mul=mul)   #store sound as player
        self.hrtf = HRTF(self.sndPlayer)  #store hrtf
    def play(self,userCoords, userAngle):
        '''plays the sound, spatialized to user's initial coords'''
        self.set_mul_and_azi(userCoords,userAngle)  #set the volume and angle of the sound initially
        self.hrtf.play()
        print('play?')
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
        elif distance > self.volRange:  #if user is outside range
            return 0
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
    def get_triggered(self):
        return self.triggered
    def user_in_range(self, userCoords):
        x1 = userCoords[0]  #get coords
        y1 = userCoords[1]
        xmin = self.roomCoords[0]
        xmax = self.roomCoords[1]
        ymin = self.roomCoords[2]
        ymax = self.roomCoords[3]
        return xmin <= x1 <= xmax and ymin <= y1 <= ymax
    def update(self, userCoords, userAngle):
        self.set_mul_and_azi(userCoords, userAngle)
        if self.triggered and not self.played and self.user_in_range(userCoords):
            self.play(userCoords, userAngle)
            self.played = True
class User():
    '''represents a user in the coordinate plane with a position and an angle
    controlled by arrow keys (up = forward, l/r = turn 90 degrees)'''
    def __init__(self, coords, footsteps):
        '''creats a user with coordinates'''
        self.x = coords[0]
        self.y = coords[1]
        self.footsteps = footsteps
        self.angle = 0  #start facing north
    def on_press(self, key):
        '''changes the user's position and angle based on keystrokes'''
        if key == keyboard.Key.left:
            self.turn(1)    #turn positive angle (left), on left keystroke
        elif key == keyboard.Key.right:
            self.turn(-1)   #turn a negative angle (right), on right keystroke
        elif key == keyboard.Key.up:
            self.move(True)    #take a step forward
        elif key == keyboard.Key.down:
            self.move(False)   #take a step back
        print(self.x, self.y, self.angle)
        footsteps.out()
    def on_release(self, key):
        '''stops the user from moving when the key is released'''
        if key == keyboard.Key.up or key == keyboard.Key.down:
            self.stop()
    def turn(self, dir):
        '''changes the user's angle slowly, 90 degrees left or right'''
        targetAngle = (self.angle + dir*90) % 360   #calculate target angle based on direction (1 or -1)
        while round(self.angle) != round(targetAngle):  #keep iterating until we iterate angle enough to get to the target
            self.angle += dir * 5              #add or subtract based on dir
            self.angle = self.angle % 360      #keep it mod 360
            time.sleep(0.1)                    #wait, so the turn happens gradually
    def move(self, forward):
        '''moves user forward/backward, in the direction the user is facing'''
        dir = 1             #make dir 1 or -1 based on the value of forward (bool)
        if not forward:
            dir = -1
        angleFromX = (90 + self.angle)*(math.pi/180)   #calculate the angle from the western x axis (bc trig)
        changeX = dir * math.cos(angleFromX)           #calculate (tiny) steps to take in x and y direction
        changeY = dir * math.sin(angleFromX)
        self.x += changeX       #iterate coords accordingly
        self.y += changeY
    def get_coords(self):
        '''returns the player's coordinates'''
        return [self.x, self.y]
    def get_angle(self):
        '''returns the players angle'''
        return self.angle


wn = turtle.Screen()
wn.setup(width=900,height=700)
wn.title("Python Turtle Movement")
wn.bgpic("downstairsHouse.gif")

def playerUp():
  # player.sety(player.ycor()+51)
  player.forward(51)
def playerDown():
  # player.sety(player.ycor()-51)
  player.backward(51)
def playerRight():
  player.right(90)
  # player.setx(player.xcor()+51.5)
  # player.right(5)
def playerLeft():
  player.left(90)
  # player.setx(player.xcor()-51.5)
  # player.left(5)
def changeUp():
  wn.bgpic("upstairsGIF.gif")

player = turtle.Turtle()
player.speed(0) #this will make your player created instantly
player.shape("arrow") #set player shape
player.color("red") #set player color
player.penup() #prevent drawing lines
player.left(90)
player.goto(348,-133) #set player location

wn.onkey(playerUp, "w") #function, key
wn.onkey(playerDown, "s")
wn.onkey(playerRight, "d")
wn.onkey(playerLeft, "a")
wn.onkey(playerUp, "Up") #function, key
wn.onkey(playerDown, "Down")
wn.onkey(playerRight, "Right")
wn.onkey(playerLeft, "Left")
wn.onkey(changeUp, "u")
wn.listen()

plr = SfPlayer("final_slowwalk1.wav", loop=True, mul = 0.2)
footsteps = HRTF(plr)

user = User([16,4], footsteps)  #make a user at 0,0
piano = Sound("final_pianopiece.wav", [10 , 5], 0.2, user, 25, 'music', loop=True)   #make the sound at -10, 0
static = Sound("final_static.wav", [15,6.5], 0.2, user, 25, 'entry', loop=True)
eating = Sound("final_monstereating.wav",[1,9],0.5, user, 10, 'kitchen',loop = True, triggered=True)
where = Sound("final_deepwhere.wav",[2,12],0.5, user, 10, 'kitchen', loop = True, triggered=True)
laugh = Sound("final_laughing.wav",[5,11],0.5, user, 10, 'kitchen',loop = True, triggered=True)
soundList = [piano, static, eating, where, laugh]


def press(key):     #make the press function
    global user
    user.on_press(key)  #it just calls the user method

listener = keyboard.Listener(on_press=press)    #make and start listener
listener.start()
for sound in soundList:
    if not sound.get_triggered():
        sound.play(user.get_coords(), user.get_angle())
        print("played")


while True:       #while its playing, constantly update the azi and mul based on user's coords and angle
    for sound in soundList:
        sound.update(user.get_coords(), user.get_angle())
    wn.update()

time.sleep(300)  #idk why this is here but it works