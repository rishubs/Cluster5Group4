from pyo import *
from pynput import keyboard
import os
import time
import math
import turtle
#import sys

#sys.setcheckinterval(200)

#make and start pyo server
s = Server(duplex=1, buffersize=4096, winhost='asio', nchnls=2).boot()
s.start()


class Sound():
    '''stores a sound file/player, and is spatialized based on
    the user's coordinates'''
    def __init__(self, filename, coords, mul,user, volRange, room, loop=True, triggered = False):
        '''makes a sound located at coords in the plane'''
        self.rooms = {'entry':[12,16,6,8],'music':[8,12,4,8],'family':[3,8,1,7],'kitchen':[0,6,7,12], \
                      'elevator':[6,8,8,12],'dining':[8,13,8,12],'bath':[8,12,8,12],'master':[],'study':[],\
                      'library':[],'balcony':[]}
        self.room = room
        self.roomCoords = self.rooms[room]
        self.stopForever = False
        self.x = coords[0]  #store the x coord of the sound
        self.y = coords[1]  #store the y coord
        self.user = user    #store the user (to use their coords later)
        self.volRange = volRange
        self.triggered = triggered
        self.elevatorHappened = False
        self.played = False
        self.name = filename
        self.sndPlayer = SfPlayer(filename,loop=loop,mul=mul)   #store sound as player
        self.hrtf = HRTF(self.sndPlayer)  #store hrtf
        self.hrtf.stop()
    def play(self,userCoords, userAngle):
        print(self.name, 'played')
        '''plays the sound, spatialized to user's initial coords'''
        self.set_mul_and_azi(userCoords,userAngle)  #set the volume and angle of the sound initially
        self.hrtf.play()
        #print('play?', self.name)
        self.hrtf.out()                             #and send it out
        print(self.hrtf.isPlaying(), self.hrtf.isOutputting(), self.hrtf.mul)
    def get_azi(self, userCoords,userAngle):
        '''returns the proper azimuth in order to spatialize the sound based on user's coords'''
        x1 = userCoords[0]  #get coords
        y1 = userCoords[1]
        dx = x1 - self.x    #calculate distance between sound and user on x and y axes
        dy = y1 - self.y
        angle = 0           #initialize angle (for scope reasons
        if dx != 0:         #only calculate if dx isnt zero (otherwise we get zero division error)
            angle = ((math.atan2(dy,dx))*(180/math.pi) - 90 - userAngle)   #calculate azi (get arctan of the slope, then convert to degrees
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
        dy = self.y - y1
        distance = math.sqrt(dx**2+dy**2)   #use pythagoras
        if distance <=1:    #if user is within 1 unit
            return 1        #as loud as possible
        elif distance > self.volRange:  #if user is outside range
            return 0
        else:
            return 1/distance   #mul is inversely proportional to user's distance
    def set_mul_and_azi(self, userCoords, userAngle):
        #print(self.name, 'set')
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
        #print(self.name, 'updated')
        self.set_mul_and_azi(userCoords, userAngle)
        if self.triggered and not self.played and self.user_in_range(userCoords) and not self.stopForever:
            #print(self.name, 'played')
            self.play(userCoords, userAngle)
            self.played = True
            if self.room == 'elevator' and not self.elevatorHappened:
                #print('elevator entered')
                changeUp()
                self.elevatorHappened = True
        if self.triggered and self.played and not self.user_in_range(userCoords):
            self.hrtf.stop()
            self.played = False
    def get_name(self):
        return self.name
    def stop(self):
        self.hrtf.stop()
        self.stopForever = True
class User():
    '''represents a user in the coordinate plane with a position and an angle
    controlled by arrow keys (up = forward, l/r = turn 90 degrees)'''
    def __init__(self, coords, footsteps):
        '''creats a user with coordinates'''
        self.x = coords[0]
        self.y = coords[1]
        self.footsteps = footsteps
        self.angle = 90  #start facing north
        self.updating = True
        self.angleChanger = Phasor(10, mul = 90)
        self.table = LinTable([(0,0),(90,90)])
        self.change = TableRead(self.table, self.angleChanger)
    def on_press(self, key):
        '''changes the user's position and angle based on keystrokes'''
        if self.updating:
            if key == keyboard.Key.left:
                self.turn(1)    #turn positive angle (left), on left keystroke
            elif key == keyboard.Key.right:
                print('right')
                self.turn(-1)   #turn a negative angle (right), on right keystroke
                print('after turn')
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
        print('turn')
        targetAngle = (self.angle + dir*90) % 360   #calculate target angle based on direction (1 or -1)
        print(self.angle, targetAngle)
        originalAngle = self.angle
        #self.angleChanger.reset()
        self.change.play()
        while round(self.angle) != round(targetAngle):  #keep iterating until we iterate angle enough to get to the target
            print(self.angle, self.angleChanger)
            print(self.change.get())
            self.angle = originalAngle + dir * self.change.get()
            print(self.angle, targetAngle)
            #print('2')
            #self.angle += dir * 5              #add or subtract based on dir
            #print('3')
            self.angle = self.angle % 360      #keep it mod 360
            #print('4')
            #time.sleep(0.07)
            #print('5')
            print(self.angle)
            #print('6')
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
    def start_updating(self):
        self.updating = True
    def stop_updating(self):
        self.updating = False

wn = turtle.Screen()
wn.setup(width=900,height=700)
wn.title("Python Turtle Movement")
wn.bgpic("downstairsHouse.gif")

def playerUp():
  # player.sety(player.ycor()+51)
  player.forward(51)
  #print('for')
def playerDown():
  # player.sety(player.ycor()-51)
  player.backward(51)
  #print('back')
def playerRight():
  player.right(90)
  #print('right')
  # player.setx(player.xcor()+51.5)
  # player.right(5)
def playerLeft():
  player.left(90)
  #print('left')
  # player.setx(player.xcor()-51.5)
  # player.left(5)
def changeUp():
  global upstairs
  wn.bgpic("upstairsGIF.gif")
  wn.update()
  #print("change up??")
  upstairs = True
  #print(upstairs)
  for sound in soundListD:
      sound.stop()
      #print(sound.get_name, 'stopped')





player = turtle.Turtle()
player.speed(0) #this will make your player created instantly
player.shape("arrow") #set player shape
player.color("red") #set player color
player.penup() #prevent drawing lines
player.left(90)
player.goto(348,-133) #set player location

plr = SfPlayer("final_slowwalk1.wav", loop=True, mul = 0.2)
footsteps = HRTF(plr)
user = User([16,7], footsteps)  #make a user at 0,0

def keysDeactivate():
    global user
    wn.onkey(None, "w") #function, key
    wn.onkey(None, "s")
    wn.onkey(None, "d")
    wn.onkey(None, "a")
    wn.onkey(None, "Up") #function, key
    wn.onkey(None, "Down")
    wn.onkey(None, "Right")
    wn.onkey(None, "Left")
    user.stop_updating()
def keysActivate():
    global user
    wn.onkey(playerUp, "w") #function, key
    wn.onkey(playerDown, "s")
    wn.onkey(playerRight, "d")
    wn.onkey(playerLeft, "a")
    wn.onkey(playerUp, "Up") #function, key
    wn.onkey(playerDown, "Down")
    wn.onkey(playerRight, "Right")
    wn.onkey(playerLeft, "Left")
    user.start_updating()


def press(key):     #make the press function
    global user
    user.on_press(key)  #it just calls the user method

listener = keyboard.Listener(on_press=press)

keysActivate()


scene1plr = SfPlayer('scene1ver2.wav', mul = 0.5)
finalScenePlr = SfPlayer('final_lastscenever2.wav', mul = 0.5)


#piano = Sound("final_pianopiece.wav", [10 , 5], 0.2, user, 25, 'music', loop=True)   #make the sound at -10, 0
piano = Sound("final_pianopiece.wav", [10 , 5], 0.2, user, 25, 'music', loop=True)
static = Sound("final_static.wav", [15,6.5], 0.2, user, 25, 'entry', loop=True)
eating = Sound("final_monstereating.wav",[1,9],0.5, user, 10, 'kitchen',loop = True, triggered=True)
where = Sound("final_deepwhere.wav",[2,12],0.5, user, 10, 'kitchen', triggered=True)
laugh = Sound("final_laughing.wav",[5,11],0.5, user, 10, 'kitchen',loop = True, triggered=True)
guitar = Sound("final_guitar1.wav",[7,5],0.7, user, 5, 'family', triggered = True)
breathing = Sound("final_heavybreathing.wav",[8,10],0.3, user, 5, 'dining', triggered=True)
dining = Sound('final_diningscene.wav', [11,10],0.3,user,5,'dining',triggered = True)
elevator = Sound("final_elevator.wav", [9,10],0.4,user,5,'elevator',triggered = True)
scratch = Sound('final_weirdscratching.wav',[9,10],0.4,user,5,'elevator',triggered = True)
drop = Sound('final_waterdrop.wav', [11,10],0.2, user,5, 'bath', triggered = True)
hum = Sound('final_humming.wav', [9,9],0.2, user, 5, 'bath', triggered=True)

constants = [piano, static]
soundListD = [eating, where, laugh, guitar, breathing, dining]
soundListU = [drop,hum]
print(guitar.is_playing())

upstairs = False

#f = input('f')
#scene1plr.out()
#time.sleep(11)
for i in range(30):
    player.forward(5.1)
    #time.sleep(float(1/3))
#time.sleep(10)
for i in range(20):
    player.left(4.5)
    #time.sleep(0.5)

wn.listen()
#make and start listener
listener.start()

for sound in constants:
    sound.play(user.get_coords(), user.get_angle())
beenUp = False

while True:       #while its playing, constantly update the azi and mul based on user's coords and angle
    #print('1')
    for sound in soundListD:
        sound.update(user.get_coords(), user.get_angle())
    #print('2')
    for sound in soundListU:
        sound.update(user.get_coords(), user.get_angle())
    elevator.update(user.get_coords(), user.get_angle())
    scratch.update(user.get_coords(), user.get_angle())
    #print('3')
    for sound in constants:
        sound.update(user.get_coords(), user.get_angle())
    #print('4')
    if upstairs and not beenUp:
        #print('nya?')
        beenUp = True
        keysDeactivate()
        #print('deactivate, been')
        time.sleep(21)
        #print('slept')
        keysActivate()
        #print('activated')
    if upstairs and user.get_coords()[1] < 7:
        #print('5')
        for sound in soundListU:
            sound.stop()
        for sound in constants:
            sound.stop()
        finalScenePlr.out()
        time.sleep(32)
        quit()
    #print('6')
    wn.update()
    #print('7')

