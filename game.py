from enum import Enum
import random
import itertools
import hashlib

def makeSalt():
  return "%064x" % random.randrange(16**64)

class Mode(Enum):
  INACTIVE = 0
  WAITING = 1
  PLAYING = 2
  REVEAL = 3

class DiceGame:
  def __init__(self):
    self.id = ""
    self.host = ""

    self.mode = Mode.INACTIVE

    self.ready = set() # List of ids who are ready
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {} # List of revealed dice

    self.diceTable = []

    self.myDice = (None, None) # (index, salt)

    self.currentBid = (0, 0)

  def handleLine(self, line):
    sp = line.split(" ", 1)
    if sp[0] == "ID":
      self.id = sp[1]
    elif sp[0] == "HOST":
      self.host = sp[1]
    else:
      userId = sp[0]
      command = sp[1].split(" ")

      if command[0] == "startRound":
        self.startRound()

      elif command[0] == "playRound":
        if self.mode == Mode.WAITING:
          self.hashes[userId] = command[1]
          self.ready = set()

      elif command[0] == "rollDice":
        if self.mode == Mode.WAITING:
          self.ready.add(userId)
          if len(self.ready) == len(self.hashes):
            self.startPlaying()

      elif command[0] == "makeBid":
        if self.mode == Mode.PLAYING:
          if self.turnOrder[self.turn] == userId:
            if command[1] == "challenge":
              self.startRevealing()
            else
              newBid = (int(command[1]), int(command[2]))
              if newBid > self.currentBid:
                self.currentBid = newBid
                self.turn = (self.turn + 1) % len(self.turnOrder)

      elif command[0] == "showDice":
        if self.mode == Mode.REVEAL:
          # Verif

  def startRound(self):
    if self.mode != Mode.INACTIVE:
      return

    self.mode = Mode.WAITING

    self.ready = set()
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {}

    self.diceTable = []

    self.myDice = (None, None)

    self.currentBid = (0, 0)

  def startPlaying(self):
    if self.mode != Mode.WAITING:
      return

    self.mode = Mode.PLAYING

    self.turnOrder = map(lambda x: x[0], self.hashes.iteritems().sorted())

    random.seed("+".join(self.hashes.values()))
    self.diceTable = itertools.product(range(1, 7), repeat=5)
    random.shuffle(self.diceTable)

  def startRevealing(self):
    if self.mode != Mode.PLAYING:
      return None

    self.mode = Mode.REVEAL

  def rollMyDice(self):
    self.myDice = (random.randint(0, 7775), makeSalt())

  def getHash(self, dice):
    m = hashlib.md5()
    m.update(str(dice[0]) + ":" + dice[1])
    return m.hexdigest()

  def getMyDice(self):
    if len(self.diceTable) == 0:
      return None
    else
      return self.diceTable[self.myDice[0]]