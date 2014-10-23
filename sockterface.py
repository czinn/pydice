from interface import DiceGameInterface
from threading import Thread
from Queue import Queue
import socket
from sys import argv

class SocketInterface(Thread):
  def __init__(self, interface, s):
    super(SocketInterface, self).__init__()

    self.s = s
    self.interface = interface
    print "Started socket"

  def run(self):
    while True:
      # Poll the socket
      line = self.s.recv(1000)

      for l in line.split("\r\n"):
        if len(l) > 0:
          self.interface.g.handleLine(l)

class UserInterface(Thread):
  def __init__(self, interface, s):
    super(UserInterface, self).__init__()
    
    self.interface = interface
    self.s = s

  def run(self):
    while True:
      # Poll the user
      line = raw_input()

      if line == "exit":
        break
      #print "Got something from the user"
      #print line
      self.interface.handleInput(line)

host = argv[1] if len(argv) >= 2 else "localhost"
port = argv[2] if len(argv) >= 3 else 31234

s = socket.create_connection((host, port))

def sendLine(line):
  s.send(line + "\r\n")

i = DiceGameInterface()
i.sendLine = sendLine

SocketInterface(i, s).start()
UserInterface(i, s).start()
