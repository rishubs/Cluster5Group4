from pyo import *

s = Server(duplex=1, buffersize=1024, winhost='asio', nchnls=2).boot()
s.start()

chairsit = "../Sounds/final_chairsit.wav"
groan = "../Sounds/final_groan.wav"
