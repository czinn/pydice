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
  def __init__(self, displayInfo):
    self.myDice = (None, None) # (index, salt)

    self.mode = INACTIVE

    self.ready = set() # List of ids who are ready
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {} # List of revealed dice
    self.currentBid = (0, 0)

    self.diceTable = []

    self.displayInfo = displayInfo

  def handleLine(self, line):
    sp = line.strip().split(" ", 1)
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
        if userId in self.hashes:
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

          if len(self.reveals) == len(self.hashes):
            self.mode = INACTIVE
            self.displayInfo("roundOver", None)
        else:
          self.displayInfo("showDiceBad", userId)

    elif command[0] == "chat":
      # Show chat message
      self.displayInfo("chat", (userId, sp[1][5:]))

    elif command[0] == "killRound":
      # Try to kill the round
      self.mode = INACTIVE
      pass

  def startRound(self):
    if self.mode != INACTIVE:
      return

    self.mode = WAITING

    self.myDice = (None, None)

    self.ready = set()
    self.hashes = {}
    self.turnOrder = []
    self.turn = 0
    self.reveals = {}
    self.currentBid = (0, 0)

    self.diceTable = []

  def startPlaying(self):
    if self.mode != WAITING:
      return

    self.mode = PLAYING

    self.turnOrder = map(lambda x: x[0], sorted(self.hashes.items(), key=lambda a: a[1]))

    rState = random.getstate()
    random.seed("+".join(self.hashes.values()))
    self.diceTable = list(itertools.product(range(1, 7), repeat=5))
    random.shuffle(self.diceTable)
    random.setstate(rState)

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

  # Returns a tuple of (winner, loser, dicePool) for the most recent game
  def getResults(self):
    if len(self.reveals) > 0:
      allDice = []
      for id in self.reveals:
        allDice.extend(self.reveals[id])
      allDice.sort()

      # Check if bidder won
      if (self.currentBid[1] == 1 and allDice.count(1) >= self.currentBid[0]) or (self.currentBid[1] != 1 and allDice.count(1) + allDice.count(self.currentBid[1]) >= self.currentBid[0]):
        return (self.turnOrder[self.turn - 1], self.turnOrder[self.turn], allDice)
      else:
        return (self.turnOrder[self.turn], self.turnOrder[self.turn - 1], allDice)