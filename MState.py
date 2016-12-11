# Module to hold the state of the game

#from GroupyComm import GroupyCommTest as GroupyComm
from MInfo import *

import random
import _thread
import time

class Player:
  
  def __init__(self,id_, role="", vote=None, target=None):
    self.id_ = id_
    self.role = role
    self.vote = vote
    self.target = target

class MState:

  """
Attributes:

comm - The Communication object used to respond to stimuli
time, day  - "Day"/"Night", number representing current day. 0 is no game
null  - A generic player object used for recording the number voting for no kill

num_mafia  - INT, number of remaining mafia
players  - A list of PLAYER objects currently in the game
nextPlayerIDs  - A list of strings representing the IDs of those in the next game

savedRoles  - A list of the roles people were assigned at the beginning of the game.
  Used to reveal roles at the end

mafia_target  - A player object that the mafia has targeted

idiot_winners  - A list of players who won by being an idiot that was voted out

timer_value  - The amount of time left when timer is on
timerOn  - if Timer is on

"""
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
    
    self.idiot_winners = []

    self.timer_value = 0
    self.timerOn = False

    self.loadNotes()

    ## initialize time keeping thread
    _thread.start_new_thread(self.watchTimer, ())
    
  def vote(self, voter_id, votee_id):
    """ Makes voter change vote to votee, then checks for lynch. """
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

  def kill(self, p):
    """ Remove player p from the game. """
    # Check if the player is represented as an object or a string
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Couldn't kill {}: {}".format(p,e))
      return False

    # Remove player from game
    try:
      if player.role in MAFIA_ROLES:
        self.num_mafia = self.num_mafia - 1
      self.players.remove(player)
    except Exception as e:
      log("Failed to kill {}: {}".format(player.id_,e))
      return False
    # Check win conditions
    if not self.checkWinCond():
      # Game continues, let the person know roles
      self.comm.sendDM(self.revealRoles(),player.id_)
    return True

  def mafiaTarget(self, target_option):
    """ Change Mafia's target to players[target_option] """
    if not self.time == "Night":
      log("Mafia couldn't target {}: Not Night".format(target_option))
      return False
    try:
      if target_option == len(self.players):
        target = null
      elif target_option == None:
        target = None
      else:
        target = self.players[target_option]
    except Exception as e:
      log("Mafia failed to target {}: {}".format(target_option, e))
      return False
    self.mafia_target = target
    self.comm.cast("It is done",MAFIA_GROUP_ID)
    # Check if Night is over
    self.checkToDay()
    return True

  def mafia_options(self):
    """ Send the mafia's options to the mafia chat. """
    msg = "Use /target number (i.e. /target 1) to select someone to kill:"
    c = 0
    for player in self.players:
      msg += "\n"+str(c)+" "+self.comm.getName(player.id_)
      c += 1
    self.comm.cast(msg,MAFIA_GROUP_ID)
    return True

  def target(self, p, target_option):
    """ Change p's target to players[target_option]. """
    if not self.time == "Night":
      log("{} couldn't target {}: Not Night".format(p,target_id))
      return False
    
    # Check if the player is represented as an object or a string
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Couldn't find target from {}: {}".format(p,e))
      return False    
    try:
      if target_option == len(self.players):
        target = self.null
      elif target_option == None:
        target = None
      else:
        target = self.players[target_option]
      player.target = target
    except Exception as e:
      log("{} failed to target {}: {}".format(player.id_, target_option, e))
      return False
    self.comm.sendDM("It is done",player.id_)
    # Check if Night is over
    self.checkToDay()
    return True

  def send_options(self, prompt, p):
    """ Send list of options to player p with preface prompt. """
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Couldn't send options to {}: {}".format(p,e))
    msg = prompt
    c = 0
    for p in self.players:
      msg += "\n"+str(c)+" "+self.comm.getName(p.id_)
      c += 1
    return self.comm.sendDM(msg,player.id_)

  def reveal(self, p):
    """ Reveal a player's role to the Main Chat """
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Could not reveal {}: {}".format(p,e))
      return False
    self.comm.cast(self.comm.getName(player.id_) + " is " + player.role)
    return True

  def checkVotes(self,p):
    """ See if there is a majority of votes for p, if so, kill p and go toNight. """
    if p == None:
      self.comm.cast("Vote Retraction successful")
      return True
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Could not check votes for {}: {}".format(p,e))
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
      if(self.kill(player.id_)):
        self.comm.remove(player.id_)
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
    """ Check if all night roles are done, if so, call toDay. """
    cop_doc_done = True
    for p in self.players:
      if p.role in ["COP","DOCTOR"] and p.target == None:
        cop_doc_done = False
    
    if (self.mafia_target == None or not cop_doc_done):
      return False
    else:
      self.toDay()
      return True

  def toDay(self):
    """ Change state to day, realizing the mafia's target and all other targets. """
    self.time = "Day"
    self.day = self.day + 1
    self.comm.cast("Uncertainty dawns, as does this day")
    # If mafia has a target
    if not self.mafia_target in [None, self.null]:
      # Doctor is alive and saved the target
      target_saved = False
      for p in self.players:
        if (p.role == "DOCTOR" and p.target.id_ == self.mafia_target.id_):
          target_saved = True
      if target_saved:
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
        self.comm.remove(self.mafia_target.id_)
    # Mafia has no target
    else:
      msg = ("A peculiar feeling drifts about... everyone is still alive...")
      self.comm.cast(msg)

    # If cop is still alive and has chosen a target
    for p in self.players:
      if p.role == "COP" and (not p.target in [None, self.null]):
        self.comm.sendDM("{} is {}".format(self.comm.getName(p.target.id_),
          "MAFIA" if (p.target.role in MAFIA_ROLES and
                      not p.target.role == "GODFATHER") else "TOWN"),
                      p.id_)
    
    self.clearTargets()
    return True

  def toNight(self):
    """ Change state to Night, send out relevant info. """
    self.time = "Night"
    for p in self.players:
      p.vote = None
    self.comm.cast("Night falls and everyone sleeps")
    self.comm.cast("As the sky darkens, so too do your intentions. Pick someone to kill",MAFIA_GROUP_ID)
    self.mafia_options()
    for p in self.players:
      if p.role == "COP":
        self.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",p.id_)
      elif p.role == "DOCTOR":
        self.send_options("Use /target number (i.e. /target 0) to pick someone to save",p.id_)
    self.setTimer()
        
  def checkWinCond(self):
    """ Check if a team has won, if so end the game. """
    # Check win conditions
    if self.num_mafia == 0:
      self.comm.cast("TOWN WINS")
      self.win = self.win + " TOWN"
      self.comm.cast("TOWN WINS",LOBBY_GROUP_ID)
      self.endGame()
      return True
    elif self.num_mafia >= len(self.players)/2:
      self.comm.cast("MAFIA WINS")
      self.win = self.win + " MAFIA"
      self.comm.cast("MAFIA WINS",LOBBY_GROUP_ID)
      self.endGame()
      return True
    return False

  def clearTargets(self):
    """ Clear all player's targets. """
    for p in self.players:
      p.target = None
    self.mafia_target = None

  def addUntil(self, role, weights):
    """ Helper for genRoles """
    result = 0
    for i in range(len(weights[0])):
      result += weights[1][i]
      if weights[0][i] == role:
        break
    return result

  def genRoles(self, num_players):
    """ Create a list of roles of length num_players. Uses random but semi-fair assignment """
    assert(num_players >= 3)
    while(True):
      n = 0
      score = BASE_SCORE
      roles = []
      num_mafia = 0
      num_town = 0
      town_sum = sum(TOWN_WEIGHTS[1])
      mafia_sum = sum(MAFIA_WEIGHTS[1])
      role = "TOWN"

      if num_players == 4:
        return ["TOWN", "DOCTOR", "COP", "MAFIA"]
      elif num_players == 3:
        return ["DOCTOR", "MAFIA", "COP"]
      while(n < num_players):
        r = random.randint(-3,3)
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
        if role == "GODFATHER":
          score -= len([None for c in roles if c == "COP"])
        if role == "COP":
          score -= len([None for g in roles if g == "GODFATHER"])
        n += 1

      # Done making roles, ensure this isn't a bad game
      if not ((num_mafia + 2 >= num_town) or (num_mafia == 0)):
        break

    # Roles contains a valid game
    print(score)
    return roles
      
  def startGame(self):
    """ Gen roles, create player objects and start the game. """
    num_players = len(self.nextPlayerIDs)
    if num_players < 3:
      self.comm.cast("Not enough players to start",LOBBY_GROUP_ID)
      return False

    self.day = 1
    self.time = "Day"

    self.comm.clearMafia()
    self.players.clear()
    self.savedRoles.clear()
    self.num_mafia = 0

    random.shuffle(self.nextPlayerIDs)
    
    roles = self.genRoles(num_players)

    for i in range(len(self.nextPlayerIDs)):
      player = Player(self.nextPlayerIDs[i], roles[i])
      self.players.append(player)

      self.savedRoles[player.id_] = player.role
      
      if player.role in MAFIA_ROLES:
        self.num_mafia += 1
      log("{} - {}".format(self.comm.getName(player.id_),player.role))

    self.nextPlayerIDs.clear()
    random.shuffle(self.players)

    self.comm.clearMain([p.id_ for p in self.players])

    for player in self.players:
      self.comm.sendDM(ROLE_EXPLAIN[player.role],player.id_)
      self.comm.addMain(player.id_)
      if player.role in MAFIA_ROLES:
        self.comm.addMafia(player.id_)

    self.comm.cast(("Dawn. Of the game and of this new day. You have learned "
                    "that scum reside in this town... A scum you must purge. "
                    "Kill Someone!"))

    return True

  def endGame(self):
    """ Reset State and end the game. """
    self.day = 0
    self.time = "Day"
    self.players.clear()
    self.comm.clearMafia()

    for winner in self.idiot_winners:
      self.comm.cast(self.comm.getName(winner.id_)+" WON!")

    self.comm.cast(self.revealRoles())
    self.comm.cast(self.revealRoles(),LOBBY_GROUP_ID)
    self.recordGame()
    return True

  def revealRoles(self):
    """ Make a string of the original roles that the game started with. """
    r = "GG, here were the roles:"
    for player_id,role in self.savedRoles.items():
      r += "\n" + self.comm.getName(player_id) + ": " + role
    return r

  def getPlayer(self, p):
    """ p can be player or id, either way returns the player object associated. """
    if type(p) == Player:
      return p
    elif type(p) == str:
      players = [player for player in self.players if player.id_ == p]
      if len(players) >= 1:
        return players[0]
      else:
        raise Exception("Couldn't find player from id {}".format(p))
    else:
      raise Exception("Couldn't find player from {}".format(p))

  def loadNotes(self):
    """ Loads all notes that were saved """
    try:
      for varName in SAVES:
        self.__dict__[varName] = loadNote(varName)
    except NoteError as e:
      log(e)

  def recordGame(self):
    m = ""
    for player_id,role in self.savedRoles.items():
      m += role + " "
    m += self.win + "\n"
    m += len(self.idiot_winners) +"\n\n"

    try:
      f = open(info_fname, 'a')
      f.write(m)
      f.close()
    except Exception as e:
      log("Failed to save game")

  def saveNotes(self):
    """ Saves all important info so the game can be recovered. """
    for varName in SAVES:
      saveNote(self.__dict__[varName],varName)

  def setTimer(self):
    """ Start a 5 minute timer. At the end of which the game will automatically progress. """
    if not (self.timerOn or self.day == 0):
      self.timerOn = True
      self.timer_value = SET_TIMER_VALUE
      self.comm.cast("Timer Started. Five minutes left")
      return True
    else:
      return False

  def watchTimer(self):
    """ Ticks a timer and switches to the next stage when we take too long. """
    lastTime = self.time
    lastDay  = self.day
    seconds = 0
    while True:
      currTime = self.time
      currDay  = self.day
      if self.timerOn:
        if((not currDay == 0) and currTime == lastTime and currDay == lastDay):
          self.timer_value -= 1
        else:
          self.timerOn = False
          self.timer_value = 0
      if self.timerOn:
        if self.timer_value == 60:
          self.comm.cast("One minute remaining, one minute")
        elif self.timer_value == 20:
          self.comm.cast("Twenty Seconds")
        elif self.timer_value == 0:
          if currTime == "Day":
            self.comm.cast("You are out of time")
            self.toNight()
            self.timerOn = False
            self.timer_value = 0
          elif currTime == "Night":
            self.comm.cast("Some people slept through the night")
            self.toDay()
            self.timerOn = False
            self.timer_value = 0

      lastTime = currTime
      lastDay  = currDay

      #Wait For a second
      time.sleep(1)

  def __str__(self):
    """ Return the status of the game. """
    if self.day == 0:
      m = "Ready to start a new game.\n"
      for p in self.nextPlayerIDs:
        m += "{}\n".format(self.comm.getName(p))
    else:
      m = "{} {}: ".format(self.time,self.day)
      if self.timerOn:
        m += time.strftime("%M:%S",time.gmtime(self.timer_value))
      m += "\n"
      for player in self.players:
        m += self.comm.getName(player.id_) + " : "
        count = 0
        for voter in [v for v in self.players if v.vote == player]:
          count += 1
          m += self.comm.getName(voter.id_) + ", "
        m += str(count) + "\n"
    return m    
