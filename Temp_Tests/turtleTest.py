import turtle

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

#update the window
while True:
  wn.update()