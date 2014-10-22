import random
import itertools
import hashlib

def makeSalt():
  return "%064x" % random.randrange(16**64)

INACTIVE = 0
WAITING = 1
PLAYING = 2
REVEAL = 3

class DiceGame:
  def __init__(self):
    self.id = ""

    self.mode = INACTIVE

    self.ready = set() # List of ids who are ready
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {} # List of revealed dice
    self.currentBid = (0, 0)

    self.diceTable = []

    self.myDice = (None, None) # (index, salt)

  def handleLine(self, line):
    sp = line.split(" ", 1)
    if sp[0] == "ID":
      self.id = sp[1]
    else:
      userId = sp[0][1:-1]
      command = sp[1].split(" ")

      if command[0] == "startRound":
        self.startRound()
        self.displayInfo("startRound", userId)

      elif command[0] == "playRound":
        if self.mode == WAITING:
          self.hashes[userId] = command[1]
          self.ready = set()
          self.displayInfo("playRound", userId)

      elif command[0] == "rollDice":
        if self.mode == WAITING:
          self.ready.add(userId)
          self.displayInfo("rollDiceVote", userId)

          if len(self.ready) == len(self.hashes):
            self.startPlaying()
            self.displayInfo("rollDice", None)
            self.displayInfo("currentTurn", None)

      elif command[0] == "makeBid":
        if self.mode == PLAYING:
          if self.turnOrder[self.turn] == userId:
            if command[1] == "challenge":
              self.startRevealing()
              self.displayInfo("challenge", userId)
            else:
              newBid = (int(command[1]), int(command[2]))
              if newBid > self.currentBid:
                self.currentBid = newBid
                self.displayInfo("makeBid", userId)

                self.turn = (self.turn + 1) % len(self.turnOrder)
                self.displayInfo("currentTurn", None)

      elif command[0] == "showDice":
        if self.mode == REVEAL:
          # Verify that dice are valid
          if self.getHash((int(command[1]), command[2])) == self.hashes[userId]:
            self.reveals[userId] = self.diceTable[int(command[1])]
            self.displayInfo("showDice", userId)

      elif command[0] == "chat":
        # Show chat message
        self.displayInfo("chat", (userId, command[1]))

      elif command[0] == "killRound":
        # Try to kill the round
        pass

  def startRound(self):
    if self.mode != INACTIVE:
      return

    self.mode = WAITING

    self.ready = set()
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {}
    self.currentBid = (0, 0)

    self.diceTable = []

    self.myDice = (None, None)

  def startPlaying(self):
    if self.mode != WAITING:
      return

    self.mode = PLAYING

    self.turnOrder = map(lambda x: x[0], sorted(self.hashes.items(), key=lambda a: a[1]))

    random.seed("+".join(self.hashes.values()))
    self.diceTable = list(itertools.product(range(1, 7), repeat=5))
    random.shuffle(self.diceTable)

  def startRevealing(self):
    if self.mode != PLAYING:
      return None

    self.mode = REVEAL

  def rollMyDice(self):
    self.myDice = (random.randint(0, 7775), makeSalt())

  def getHash(self, dice):
    m = hashlib.md5()
    m.update(str(dice[0]) + ":" + dice[1])
    return m.hexdigest()

  def getMyDice(self):
    if len(self.diceTable) == 0:
      return None
    else:
      return self.diceTable[self.myDice[0]]

  def displayInfo(self, event, data):
    if event == "startRound":
      print "%s started a new round." % data

    elif event == "playRound":
      print "%s will play this round." % data

    elif event == "rollDiceVote":
      print "%s voted to roll the dice." % data

    elif event == "rollDice":
      print "The game has begun! Your dice: %d %d %d %d %d" % self.getMyDice()

    elif event == "currentTurn":
      print "Current turn: %s" % self.turnOrder[self.turn]

    elif event == "makeBid":
      print data + " bids %d %ds" % (self.currentBid[0], self.currentBid[1])

    elif event == "challenge":
      print data + " challenges " + self.turnOrder[self.turn - 1] + "'s bid of %d %ds" % (self.currentBid[0], self.currentBid[1])

    elif event == "showDice":
      print data + " reveals %d %d %d %d %d" % self.reveals[data]

    elif event == "chat":
      print "<%s> %s" % data
