# Module to hold the state of the game

#from GroupyComm import GroupyCommTest as GroupyComm
from MInfo import *

import random
import _thread
import time

class Player:
  """
Vote is normally another player. If it is None, there is no vote yet,
if it is self.__null, it is a vote for nokill.
Target is similar.
"""
  def __init__(self,id_,role="",vote=None,target=None):
    self.id_ = id_
    self.role = role
    self.vote = vote
    self.target = target

  def __str__(self):
    return "[{}, {}]".format(self.id_,self.role)

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
  def __init__(self,comm, restart=False):
    log("MState init",3)

    self.comm = comm

    self.null = Player("0","null")

    self.time = "Day"
    self.day = 0

    self.num_mafia = 0
    self.players = []
    self.nextPlayerIDs = []

    self.savedRoles = {}

    self.mafia_target = None

    self.idiot_winners = []

    self.timer_value = 0
    self.timerOn = False


    if not restart:
      self.__loadNotes()

    _thread.start_new_thread(self.__watchTimer,())

  def vote(self,voter_id,votee_id):
    """ Makes voter change vote to votee, then checks for lynch. """
    log("MState vote",3)
    if not self.time == "Day":
      log("{} couldn't vote for {}: Not Day".format(voter_id,votee_id))
      self.comm.cast("Can't vote at Night")
      return True
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
    self.__checkVotes(votee)
    return True

  def mafiaTarget(self,target_option):
    """ Change Mafia's target to players[target_option] """
    log("MState mafiaTarget",3)
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
    self.comm.cast("It is done",MAFIA_GROUP_ID)
    # Check if Night is over
    self.__checkToDay()
    return True

  def mafia_options(self):
    """ Send the mafia's options to the mafia chat. """
    log("MState mafia_options",3)
    msg = "Use /target number (i.e. /target 1) to select someone to kill:"
    c = 0
    for player in self.players:
      msg += "\n"+str(c)+" "+self.comm.getName(player.id_)
      c += 1
    self.comm.cast(msg,MAFIA_GROUP_ID)
    return True

  def target(self,p,target_option):
    """ Change p's target to players[target_option]. """
    log("MState target",3)
    if not self.time == "Night":
      log("{} couldn't target {}: Not Night".format(p,target_option))
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
    self.__checkToDay()
    return True

  def send_options(self,prompt,p):
    """ Send list of options to player p with preface prompt. """
    log("MState send_options",3)
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

  def reveal(self,p):
    """ Reveal a player's role to the Main Chat """
    log("MState reveal",3)
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Could not reveal {}: {}".format(p,e))
      return False
    self.comm.cast(self.comm.getName(player.id_) + " is " + player.role)
    return True

  def startGame(self,testRoles=None):
    """ Gen roles, create player objects and start the game. """
    log("MState startGame",3)
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

    if testRoles == None:
      random.shuffle(self.nextPlayerIDs)
    
    roles = self.__genRoles(num_players)

    if not testRoles == None:
      for i in range(min(len(testRoles),len(roles))):
        roles[i] = testRoles[i]

    for i in range(len(self.nextPlayerIDs)):
      player = Player(self.nextPlayerIDs[i], roles[i])
      self.players.append(player)

      self.savedRoles[player.id_] = player.role
      
      if player.role in MAFIA_ROLES:
        self.num_mafia += 1
      log("{} - {}".format(self.comm.getName(player.id_),player.role))

    self.nextPlayerIDs.clear()

    if testRoles == None:
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

  def inNext(self,player_id):
    """Add a player to the next game"""
    log("MState inNext",3)
    if player_id not in self.nextPlayerIDs:
      self.nextPlayerIDs.append(player_id)
      msg = "{} added to next game:".format(self.comm.getName(player_id))
    else:
      msg = "You are already in the next game:"
    for p_id in self.nextPlayerIDs:
      msg = msg + "\n" + self.comm.getName(p_id)
    self.comm.cast(msg,LOBBY_GROUP_ID)
    return True

  def getPlayer(self, p):
    """ p can be player or id, either way returns the player object associated. """
    log("MState getPlayer",5)
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

  def setTimer(self):
    """ Start a 5 minute timer. At the end of which the game will automatically progress. """
    log("MState setTimer",3)
    if not (self.timerOn or self.day == 0):
      self.timerOn = True
      self.timer_value = SET_TIMER_VALUE
      self.comm.cast("Timer Started. Five minutes left")
      return True
    else:
      return False

  def saveNotes(self):
    """ Saves all important info so the game can be recovered. """
    log("MState saveNotes",3)
    for varName in SAVES:
      saveNote(self.__dict__[varName],varName)

  #### HELPER FN ####

  def __kill(self, p):
    """ Remove player p from the game. """
    log("MState __kill",4)
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
      log("Failed to kill {}: {}".format(player,e))
      return False
    # Check win conditions
    if not self.__checkWinCond():
      # Game continues, let the person know roles
      self.comm.sendDM(self.__revealRoles(),player.id_)
    return True

  def __checkVotes(self,p):
    """ See if there is a majority of votes for p, if so, kill p and go toNight."""
    log("MState __checkVotes",4)
    if p == None:
      self.comm.cast("Vote Retraction successful")
      return True
    try:
      player = self.getPlayer(p)
    except Exception as e:
      log("Could not check votes for {}: {}".format(p,e))
    num_voters = len([v for v in self.players if v.vote == player])
    num_players = len(self.players)
    if player == self.null:
      if num_voters >= num_players/2:
        self.comm.cast("You have decided not to kill anyone")
        self.__toNight()
        return True
      else:
        self.comm.cast("Vote successful: {} more vote{}to decide not to kill".format(
                  int((num_players+1)/2) - num_voters,
                  " " if (int((num_players+1)/2) - num_voters == 1) else "s "))
        return True  
    if num_voters > num_players/2:
      self.comm.cast("The vote to kill {} has passed".format(
                self.comm.getName(player.id_)))
      if(self.__kill(player)):
        self.comm.remove(player.id_)
        if player.role == "IDIOT":
          self.idiot_winners.append(player)
        if not self.day == 0:
          self.__toNight()
    else:
      self.comm.cast("Vote successful: {} more vote{}until {} is killed".format(
           int((num_players)/2+1)-num_voters,
           " " if int((num_players)/2+1)-num_voters == 1 else "s ",
           self.comm.getName(player.id_) ))
      return True

  def __checkToDay(self):
    """ Check if all night roles are done, if so, call toDay. """
    log("MState __checkToDay",4)
    cop_doc_done = True
    for p in self.players:
      if p.role in ["COP","DOCTOR"] and p.target == None:
        cop_doc_done = False
    
    if (self.mafia_target == None or not cop_doc_done):
      return False
    else:
      self.__toDay()
      return True

  def __toDay(self):
    """ Change state to day, realizing the mafia's target and all other targets. """
    log("MState __toDay",4)
    self.time = "Day"
    self.day = self.day + 1
    self.comm.cast("Uncertainty dawns, as does this day")
    # If mafia has a target
    if not self.mafia_target in [None, self.null]:
      # Doctor is alive and saved the target
      target_saved = False
      for p in self.players:
        if (p.role == "DOCTOR" and not p.target == None and
            p.target.id_ == self.mafia_target.id_):
          target_saved = True
      if target_saved:
          msg = ("Tragedy has struck! {} is ... wait! They've been saved by "
               "the doctor! Someone must pay for this! Vote to kill "
               "somebody!").format(self.comm.getName(self.mafia_target.id_))
          self.comm.cast(msg)
      # Doctor couldn't save the target
      else:
        self.__kill(self.mafia_target)
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
    
    self.__clearTargets()
    self.timerOn = False
    return True
  
  def __toNight(self):
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
    return True

  def __clearTargets(self):
    """ Clear all player's targets. """
    log("MState __clearTargets",4)
    for p in self.players:
      p.target = None
    self.mafia_target = None

  def __checkWinCond(self):
    """ Check if a team has won, if so end the game. """
    log("MState __checkWinCond",4)
    # Check win conditions
    if self.num_mafia == 0:
      self.comm.cast("TOWN WINS")
      self.comm.cast("TOWN WINS",LOBBY_GROUP_ID)
      self.__endGame()
      return True
    elif self.num_mafia >= len(self.players)/2:
      self.comm.cast("MAFIA WINS")
      self.comm.cast("MAFIA WINS",LOBBY_GROUP_ID)
      self.__endGame()
      return True
    return False

  def __endGame(self):
    """ Reset State and end the game. """
    log("MState __endGame",4)
    self.day = 0
    self.time = "Day"
    self.timerOn = False
    self.players.clear()
    self.comm.clearMafia()

    for winner in self.idiot_winners:
      self.comm.cast(self.comm.getName(winner.id_)+" WON!")
    self.idiot_winners.clear()
    self.comm.cast(self.__revealRoles(),LOBBY_GROUP_ID)
    return True

  def __revealRoles(self):
    """ Make a string of the original roles that the game started with. """
    log("MState __revealRoles",4)
    r = "GG, here were the roles:"
    for player_id,role in self.savedRoles.items():
      r += "\n" + self.comm.getName(player_id) + ": " + role
    return r

 

  def __addUntil(self, role, weights):
    """ Helper for genRoles """
    log("MState __addUntil",5)
    result = 0
    for i in range(len(weights[0])):
      result += weights[1][i]
      if weights[0][i] == role:
        break
    return result

  def __genRoles(self, num_players):
    """ Create a list of roles of length num_players. Uses random but semi-fair assignment """
    log("MState __genRoles",4)
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
            if t < self.__addUntil(trole,TOWN_WEIGHTS):
              role = trole
              break
          num_town += 1
        else:
          # Add Mafia
          m = random.randint(0,mafia_sum)
          for mrole in MAFIA_WEIGHTS[0]:
            if m < self.__addUntil(mrole,MAFIA_WEIGHTS):
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
    return roles
  
  def __loadNotes(self):
    """ Loads all notes that were saved """
    log("MState __loadNotes",4)
    try:
      for varName in SAVES:
        self.__dict__[varName] = loadNote(varName)
    except NoteError as e:
      log(e)

  def __watchTimer(self):
    """ Ticks a timer and switches to the next stage when we take too long. """
    log("MState __watchTimer",5)
    lastTime = self.time
    lastDay  = self.day
    while True:
      log("MState __watchTimer TICK",6)
      try:
        currTime = self.time
        currDay  = self.day
        if self.timerOn:
          if((not currDay == 0) and currTime == lastTime and currDay == lastDay):
            self.timer_value -= 1
        if self.timerOn:
          if self.timer_value == 60:
            self.comm.cast("One minute remaining, one minute")
          elif self.timer_value == 20:
            self.comm.cast("Twenty Seconds")
          elif self.timer_value == 0:
            if currTime == "Day":
              self.comm.cast("You are out of time")
              self.__toNight()
              self.timerOn = False
              self.timer_value = 0
            elif currTime == "Night":
              self.comm.cast("Some people slept through the night")
              self.__toDay()
              self.timerOn = False
              self.timer_value = 0

        lastTime = currTime
        lastDay  = currDay

        #Wait For a second
        time.sleep(1)
      except Exception as e:
        log("Error with __watchTimer: {}".format(e))

  def __str__(self):
    """ Return the status of the game. """
    log("MState __str__",5)
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
    
