import turtle

wn = turtle.Screen()
wn.setup(width=700,height=400)
wn.title("Python Turtle Movement")
wn.bgpic("downstairsHouse.gif")

def playerUp():
  player.sety(player.ycor()+51)
  # player.forward(5)
def playerDown():
  player.sety(player.ycor()-51)
  # player.backward(5)
def playerRight():
  player.setx(player.xcor()+51.5)
  # player.right(5)
def playerLeft():
  player.setx(player.xcor()-51.5)
  # player.left(5)

player = turtle.Turtle()
player.speed(0) #this will make your player created instantly
player.shape("square") #set player shape
player.color("red") #set player color
player.penup() #prevent drawing lines
player.goto(348,-133) #set player location

wn.onkey(playerUp, "w") #function, key
wn.onkey(playerDown, "s")
wn.onkey(playerRight, "d")
wn.onkey(playerLeft, "a")
wn.onkey(playerUp, "Up") #function, key
wn.onkey(playerDown, "Down")
wn.onkey(playerRight, "Right")
wn.onkey(playerLeft, "Left")
wn.listen()

#update the window
while True:
  wn.update()