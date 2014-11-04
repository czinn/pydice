import hashlib

STAGE_D = 0 # Waiting for Ds
STAGE_C = 1 # Waiting for Cs
STAGE_K = 2 # Waiting for Ks

def addHex(a, b):
  line = hex(int(a, 16) + int(b, 16))[2:]
  if line[-1] == "L":
    line = line[:-1]

  return line

class Scheme:
  def __init__(self):
    self.stage = STAGE_D
    self.d = {}
    self.c = {}
    self.k = {}
    self.S = None
    self.t = {}

  def addD(self, user, di):
    if self.stage == STAGE_D:
      self.d[user] = di
      return True

  def startC(self):
    if self.stage == STAGE_D:
      self.stage = STAGE_C

  def addC(self, user, ci):
    if self.stage == STAGE_C:
      # Check that hash(ci) == di
      if user in self.d and self.hash(ci) == self.d[user]:
        self.c[user] = ci
        return True
      else:
        return False

  def startK(self):
    if self.stage == STAGE_C:
      self.stage = STAGE_K

      # Calculate S
      sumC = "0"
      for user in self.c:
        sumC = addHex(sumC, self.c[user])
      self.S = self.hash(sumC)

      # Calculate t for all players
      for user in self.c:
        self.t[user] = self.hash(addHex(self.S, self.c[user]))

  # Gets the list of users in turn order
  def getOrder(self):
    return map(lambda x: x[0], sorted(self.t.items(), key=lambda a: a[1]))

  def addK(self, user, ki):
    if self.stage == STAGE_K:
      # Check that hash(ki) == ci
      if user in self.c and self.hash(ki) == self.c[user]:
        self.k[user] = ki
        return True
      else:
        return False

  def getR(self, k):
    if self.S:
      return self.hash(addHex(self.S, k))

  def hash(self, line):
    if line[:2] == "0x":
      line = line[2:]
    if line[-1] == "L":
      line = line[:-1]

    m = hashlib.sha256()
    m.update(line)
    return m.hexdigest()