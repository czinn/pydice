from game import DiceGame

class DiceGameInterface:
  def __init__(self):
    self.g = DiceGame(self.displayInfo)

  # Override to change output
  def displayInfo(self, event, data):
    if event == "startRound":
      print "%s started a new round." % data

    elif event == "playRound":
      print "%s will play this round." % data

    elif event == "rollDiceVote":
      print "%s voted to roll the dice." % data

    elif event == "rollDice":
      print "The game has begun! Your dice: %d %d %d %d %d" % self.g.getMyDice()

    elif event == "currentTurn":
      print "Current turn: %s" % self.g.turnOrder[self.g.turn]

    elif event == "makeBid":
      print data + " bids %d %ds" % (self.g.currentBid[0], self.g.currentBid[1])

    elif event == "challenge":
      print data + " challenges " + self.g.turnOrder[self.g.turn - 1] + "'s bid of %d %ds" % (self.g.currentBid[0], self.g.currentBid[1])
      # Important: respond to challenges by showing dice
      self.sendLine("showDice %d %s" % self.g.myDice)

    elif event == "showDice":
      print data + " reveals %d %d %d %d %d" % self.g.reveals[data]

    elif event == "chat":
      print "<%s> %s" % data

    elif event == "roundOver":
      winner, loser, allDice = self.g.getResults()
      print "%s won and %s lost. All dice: %s" % (winner, loser, " ".join(map(str, allDice)))

  # Override to change method of sending data
  def sendLine(self, line):
    print "[ SENDING \"%s\" ]" % line
    self.g.handleLine("<asdf> %s" % line)

  def handleInput(self, line):
    if line[0] == "/":
      command = line[1:].split(" ")
      if command[0] == "start" or command[0] == "startRound":
        self.sendLine("startRound")

      elif command[0] == "play" or command[0] == "playRound":
        self.g.rollMyDice()
        self.sendLine("playRound %s" % self.g.getHash(self.g.myDice))

      elif command[0] == "roll" or command[0] == "rollDice":
        self.sendLine("rollDice")

      elif command[0] == "bid" or command[0] == "makeBid":
        self.sendLine("makeBid %s %s" % (command[1], command[2]))

      elif command[0] == "challenge" or command[0] == "liar":
        self.sendLine("makeBid challenge")

      elif command[0] == "killRound" or command[0] == "restart":
        self.sendLine("killRound")

    else:
      self.sendLine("chat %s" % line)