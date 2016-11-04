# Module to hold the state of the game

#from GroupyComm import GroupyCommTest as GroupyComm
from MInfo import *

import random

class Player:

  def __init__(self,id_, role="", vote=None, target=None):
    self.id_ = id_
    self.role = role
    self.vote = vote
    self.target = target

class MState:

  def __init__(self, comm):
    self.comm = comm
    
    self.time = "Day"
    self.day = 0

    self.null = Player("0","null")

    self.num_mafia = 0
    self.players = []
    self.nextPlayerIDs = []

    self.savedRoles = {}

    self.mafia_target = None

    self.cops = []
    self.docs = []
    
    self.idiot_winners = []
    
  def vote(self, voter_id, votee_id):

    if not self.time == "Day":
      log("{} couldn't vote for {}: Not Day".format(voter_id,votee_id))
      return False

    try:
      voter = self.getPlayer(voter_id)
      if votee_id == None:
        votee = None
      elif votee_id == "0":
        votee = self.null
      else:
        votee = self.getPlayer(votee_id)
    except Exception as e:
      log(e)
      return False
    voter.vote = votee
    self.checkVotes(votee)
    return True

  def kill(self, player):
    # Remove from players things
    try:
      if player.role in MAFIA_ROLES:
        self.num_mafia = self.num_mafia - 1
      self.players.remove(player)
    except Exception as e:
      log("Failed to kill {}: {}".format(player,e))
      return False
    # Check win conditions
    if not self.checkWinCond():
      # Game continues, let the person know roles
      self.comm.sendDM(self.revealRoles(),player.id_)
    return True

  def mafiaTarget(self, target_option):
    if not self.time == "Night":
      log("Mafia couldn't target {}: Not Night".format(target_option))
      return False
    try:
      if target_option == len(self.players):
        target = self.null
      elif target_option == None:
        target = None
      else:
        target = self.players[target_option]
    except Exception as e:
      log("Mafia failed to target {}: {}".format(target_option, e))
      return False
    self.mafia_target = target
    # Check if Night is over
    self.checkToDay()
    return True

  def target(self, player_id, target_option):
    # Set a player's target. This only has an effect if the
    # player is a cop or a doc

    if not self.time == "Night":
      log("{} couldn't target {}: Not Night".format(player_id,target_id))
      return False
    try:
      if target_option == len(self.players):
        target = self.null
      elif target_option == None:
        target = None
      else:
        target = self.players[target_option]
    except Exception as e:
      log("{} failed to target {}: {}".format(player_id, target_id, e))
      return False
    player.target = target
    # Check if Night is over
    self.checkToDay()
    return True

  def checkVotes(self,player):
    if player == None:
      self.comm.cast("Vote Retraction successful")
      return True 
    voters = [v for v in self.players if v.vote == player]
    num_voters = len(voters)
    num_players = len(self.players)
    if player == self.null:
      if num_voters >= num_players/2:
        self.comm.cast("You have decided not to kill anyone")
        self.toNight()
        return True
      else:
        self.comm.cast("Vote successful: {} more vote{}to decide not to kill".format(
                  int((num_players+1)/2) - num_voters,
                  " " if (int((num_players+1)/2) - num_voters == 1) else "s "))
        return True  
    if len(voters) > num_players/2:
      self.comm.cast("The vote to kill {} has passed".format(
                self.comm.getName(player.id_)))
      if(self.kill(player)):
        if player.role == "IDIOT":
          self.idiot_winners.append(player)
        if not self.day == 0:
          self.toNight()
    else:
      self.comm.cast("Vote successful: {} more vote{}until {} is killed".format(
           int((num_players)/2+1)-num_voters,
           " " if int((num_players)/2+1)-num_voters == 1 else "s ",
           self.comm.getName(player.id_) ))
      return True

  def checkToDay(self):
    if (self.mafia_target == None or
        any([c.target == None for c in self.cops]) or
        any([d.target == None for d in self.docs])):
      return False
    else:
      self.toDay()

  def toDay(self):
    self.time = "Day"
    self.day = self.day + 1
    self.comm.cast("Uncertainty dawns, as does this day")
    # If mafia has a target
    if not self.mafia_target in [None, self.null]:
      # Doctor is alive and saved the target
      if any([d.target == self.mafia_target for d in self.docs]):
        msg = ("Tragedy has struck! {} is ... wait! They've been saved by "
               "the doctor! Someone must pay for this! Vote to kill "
               "somebody!").format(self.comm.getName(self.mafia_target.id_))
        self.comm.cast(msg)
      # Doctor couldn't save the target
      else:
        self.kill(self.mafia_target)
        msg = ("Tragedy has struck! {} is dead! Someone must pay for this! "
               "Vote to kill somebody!").format(self.comm.getName(self.mafia_target.id_))
        self.comm.cast(msg)

    # If cop is still alive and has chosen a target
    for cop in self.cops:
      if not cop.target == self.null:
        self.comm.sendDM("{} is {}".format(self.comm.getName(cop.target.id_),
            "MAFIA" if cop.target.role in MAFIA_ROLES else "TOWN"),
             cop.id_)
    
    self.mafia_target = None
    for p in self.players:
      p.target = None
    return True

  def toNight(self):
    self.time = "Night"
    for p in self.players:
      p.vote = None
    self.comm.cast("Night falls and everyone sleeps")
    self.comm.cast("As the sky darkens, so too do your intentions. Pick someone to kill",MAFIA_GROUP_ID)
    self.mafia_options()
    for cop in self.cops:
      if cop in self.players:
        self.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",cop.id_)
    for doc in self.docs:
      if doc in self.players:
        self.send_options("Use /target number (i.e. /target 0) to pick someone to save",doc.id_)

  def mafia_options(self):
    msg = "Use /target number (i.e. /target 1) to select someone to kill:"
    c = 0
    for player in self.players:
      msg += "\n"+str(c)+self.comm.getName(player.id_)
      c += 1
    self.comm.cast(msg,MAFIA_GROUP_ID)
    return True

  def send_options(self, prompt, player_id):
    msg = prompt
    c = 0
    for player in self.players:
      msg += "\n"+str(c)+self.comm.getName(player.id_)
      c += 1
    self.comm.sendDM(msg,player_id)
    return True
        
  def checkWinCond(self):
    # Check win conditions
    if self.num_mafia == 0:
      self.comm.cast("TOWN WINS")
      self.endGame()
      return True
    elif self.num_mafia >= len(self.players)/2:
      self.comm.cast("MAFIA WINS")
      self.endGame()
      return True
    return False

  def addUntil(self, role, weights):
    """Helper for genRoles"""
    result = 0
    for i in range(len(weights[0])):
      result += weights[1][i]
      if weights[0][i] == role:
        break
    return result

  def genRoles(self, num_players):
    assert(num_players >= 3)
    while(True):
      n = 0
      score = BASE_SCORE
      roles = []
      num_mafia = 0
      num_town = 0
      town_sum = sum(TOWN_WEIGHTS[1])
      mafia_sum = sum(MAFIA_WEIGHTS[1])

      if num_players == 4:
        return ["TOWN", "DOCTOR", "COP", "MAFIA"]
      elif num_players == 3:
        return ["DOCTOR", "MAFIA", "COP"]
      while(n < num_players):
        r = random.randint(-5,5)
        if r >= score:
          # Add Town
          t = random.randint(0,town_sum)
          for trole in TOWN_WEIGHTS[0]:
            if t < self.addUntil(trole,TOWN_WEIGHTS):
              role = trole
              break
          num_town += 1
        else:
          # Add Mafia
          m = random.randint(0,mafia_sum)
          for mrole in MAFIA_WEIGHTS[0]:
            if m < self.addUntil(mrole,MAFIA_WEIGHTS):
              role = mrole
              break
          if not role == "IDIOT":
            num_mafia += 1
        roles.append(role)
        score += ROLE_SCORES[role]
        n += 1

      # Done making roles, ensure this isn't a bad game
      if not ((num_mafia + 2 >= num_town) or (num_mafia == 0)):
        break

    # Roles contains a valid game
    return roles
      
  def startGame(self):
    num_players = len(self.nextPlayerIDs)
    if num_players < 3:
      self.comm.cast("Not enough players to start")
      return False

    self.day = 1
    self.time = "Day"

    self.comm.clearMafia()
    self.players.clear()
    self.cops.clear()
    self.docs.clear()
    self.idiot_winners.clear()
    self.savedRoles.clear()
    self.num_mafia = 0

    random.shuffle(self.nextPlayerIDs)
    
    roles = self.genRoles(num_players)

    for i in range(len(self.nextPlayerIDs)):
      player = Player(self.nextPlayerIDs[i], roles[i])
      self.players.append(player)

      self.savedRoles[player.id_] = player.role
      
      if player.role == "COP":
        self.cops.append(player)
      elif player.role == "DOCTOR":
        self.docs.append(player)
      elif player.role == "MAFIA":
        self.num_mafia += 1
      log("{} - {}".format(self.comm.getName(player.id_),player.role))

    self.nextPlayerIDs.clear()
    random.shuffle(self.players)

    for player in self.players:
      self.comm.sendDM(ROLE_EXPLAIN[player.role],player.id_)
      if player.role in MAFIA_ROLES:
        self.comm.addMafia(player.id_)
    return True

  def endGame(self):
    self.day = 0
    self.time = "Day"
    self.players.clear()
    self.comm.clearMafia()

    for winner in idiot_winners:
      self.comm.cast(self.comm.getName(winner.id_)+" WON!")

    self.comm.cast(self.revealRoles())
    return True

  def revealRoles(self):
    r = "GG, here were the roles:"
    for player_id,role in self.savedRoles.items():
      r += "\n" + self.comm.getName(player_id) + ": " + role
    return r

  def getPlayer(self, player_id):
    players = [p for p in self.players if p.id_ == player_id]
    if len(players) >= 1:
      return players[0]
    else:
      raise Exception("Couldn't find player from id {}".format(player_id))

  def loadNotes(self):
    try:
      for varName in SAVES:
        self.__dict__[varName] = loadNote(varName)
      self.players = self.loadPList("players")
      self.cops    = self.loadPList("cops")
      self.docs    = self.loadPList("docs")
      self.idiot_winners = self.loadPList("idiot_winners")
    except NoteError as e:
      log(e)

  def saveNotes(self):
    for varName in SAVES:
      saveNote(self.__dict__[varName],varName)
    self.savePList(self.players,"players")
    self.savePList(self.cops,"cops")
    self.savePList(self.docs,"docs")
    self.savePList(self.idiot_winners,"idiot_winners")

  def loadPList(self,name):
    ids = loadNote(name)
    plist = []
    for id_ in ids:
      p = Player(id_, loadNote(id_+"/role"),
                      loadNote(id_+"/vote"),
                      loadNote(id_+"/target"))
      plist.append(p)
    return plist

  def savePList(self,plist,name):
    ids = [p.id_ for p in plist]
    saveNote(ids,name)
    for player in self.players:
      saveNote(player.role,player.id_+"/role")
      saveNote(player.vote,player.id_+"/vote")
      saveNote(player.target,player.id_+"/target")

  def __str__(self):
    if self.day == 0:
      m = "In the next game:\n"
      for pid in self.nextPlayerIDs:
        m += self.comm.getName(pid) + "\n"
    else:
      m = "{} {}:\n".format(self.time,self.day)
      for player in self.players:
        m += self.comm.getName(player.id_) + " : "
        count = 0
        for voter in [v for v in self.players if v.vote == player]:
          count += 1
          m += self.comm.getName(voter.id_) + ", "
        m += str(count) + "\n"
    return m    
