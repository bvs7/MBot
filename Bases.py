#!/usr/bin/python3

# Base Classes for each required class. These are implemented as test classes

from MInfo import *

import _thread
import time

class GroupyCommTest:

  def __init__(self):
    log("BaseGroupyComm Init",3)

    self.main = []
    self.mafia = []

  def cast(self,msg,group_id=MAIN_GROUP_ID):
    log("BaseGroupyComm cast",3)
    m = "CAST: "
    if group_id == MAIN_GROUP_ID:
      m += "(MAIN) "
    elif group_id == MAFIA_GROUP_ID:
      m += "(MAFIA) "
    elif group_id == LOBBY_GROUP_ID:
      m += "(LOBBY) "
    m += msg

    log(m,1)
    return True

  def sendDM(self,msg,player_id):
    log("BaseGroupyComm sendDM",3)
    log("DM: "+"("+player_id+") "+msg)
    return True

  def getDMs(self,player_id):
    log("BaseGroupyComm getDMs",3)
    return []

  def getName(self,player_id):
    log("BaseGroupyComm getName",3)
    return "[Name of {}]".format(player_id)

  def getMembers(self):
    log("BaseGroupyComm getMembers",3)
    print("Getting Members")
    return []

  def addMafia(self, player_id):
    log("BaseGroupyComm addMafia",3)
    self.mafia.append(player_id)
    return True

  def clearMafia(self):
    log("BaseGroupyComm clearMafia",3)
    self.mafia.clear()
    return True

  def addMain(self, player):
    log("BaseGroupyComm addMain",3)
    if not player in self.main:
      self.main.append(player)
    return True

  def clearMain(self, saveList = []):
    log("BaseGroupyComm clearMain",3)
    for p in self.main:
      if not p in saveList:
        self.main.remove(p)
    return True

  def remove(self, p_id):
    log("BaseGroupyComm remove",3)
    if p_id in self.main:
      self.main.remove(p_id)
    if p_id in self.mafia:
      self.mafia.remove(p_id)
    return True


  def intro(self):
    log("intro")

  def outro(self):
    log("outro")

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
  def __init__(self,comm):
    log("BaseMState init",3)

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


    self.__loadNotes()

    _thread.start_new_thread(self.__watchTimer,())

  def vote(self,voter_id,votee_id):
    """ Makes voter change vote to votee, then checks for lynch. """
    log("BaseMState vote",3)
    if not self.time == "Day":
      log("{} couldn't vote for {}: Not Day".format(voter_id,votee_id))
      self.comm.cast("Can't vote at Night")
      return True
    try:
      voter = self.__getPlayer(voter_id)
      if votee_id == None:
        votee = None
      elif votee_id == "0":
        votee = self.null
      else:
        votee = self.__getPlayer(votee_id)
    except Exception as e:
      log(e)
      return False
    voter.vote = votee
    self.__checkVotes(votee)
    return True

  def mafiaTarget(self,target_option):
    """ Change Mafia's target to players[target_option] """
    log("BaseMState mafiaTarget",3)
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
    log("BaseMState mafia_options",3)
    msg = "Use /target number (i.e. /target 1) to select someone to kill:"
    c = 0
    for player in self.players:
      msg += "\n"+str(c)+" "+self.comm.getName(player.id_)
      c += 1
    self.comm.cast(msg,MAFIA_GROUP_ID)
    return True

  def target(self,p,target_option):
    """ Change p's target to players[target_option]. """
    log("BaseMState target",3)
    if not self.time == "Night":
      log("{} couldn't target {}: Not Night".format(p,target_option))
      return False
    
    # Check if the player is represented as an object or a string
    try:
      player = self.__getPlayer(p)
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
    log("BaseMState send_options",3)
    try:
      player = self.__getPlayer(p)
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
    log("BaseMState reveal",3)
    try:
      player = self.__getPlayer(p)
    except Exception as e:
      log("Could not reveal {}: {}".format(p,e))
      return False
    self.comm.cast(self.comm.getName(player.id_) + " is " + player.role)
    return True

  def startGame(self):
    """ Gen roles, create player objects and start the game. """
    log("BaseMState startGame",3)
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
    
    roles = self.__genRoles(num_players)

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

  def inNext(self,player_id):
    """Add a player to the next game"""
    log("BaseMState inNext",3)
    if player_id not in self.nextPlayerIDs:
      self.nextPlayerIDs.append(player_id)
      msg = "{} added to next game:\n".format(self.comm.getName(player_id))
    else:
      self.comm.cast("You are already in the next game:",LOBBY_GROUP_ID)
    for player in self.nextPlayerIDs:
      msg = msg + self.comm.getName(player_id) + "\n"
    self.comm.cast(msg,LOBBY_GROUP_ID)
    return True

  def setTimer(self):
    """ Start a 5 minute timer. At the end of which the game will automatically progress. """
    log("BaseMState setTimer",3)
    if not (self.timerOn or self.day == 0):
      self.timerOn = True
      self.timer_value = SET_TIMER_VALUE
      self.comm.cast("Timer Started. Five minutes left")
      return True
    else:
      return False

  def saveNotes(self):
    """ Saves all important info so the game can be recovered. """
    log("BaseMState saveNotes",3)
    for varName in SAVES:
      saveNote(self.__dict__[varName],varName)

  #### HELPER FN ####

  def __kill(self, p):
    """ Remove player p from the game. """
    log("BaseMState __kill",4)
    # Check if the player is represented as an object or a string
    try:
      player = self.__getPlayer(p)
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
    log("BaseMState __checkVotes",4)
    if p == None:
      self.comm.cast("Vote Retraction successful")
      return True
    try:
      player = self.__getPlayer(p)
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
        if not self.__day == 0:
          self.__toNight()
    else:
      self.comm.cast("Vote successful: {} more vote{}until {} is killed".format(
           int((num_players)/2+1)-num_voters,
           " " if int((num_players)/2+1)-num_voters == 1 else "s ",
           self.comm.getName(player.id_) ))
      return True

  def __checkToDay(self):
    """ Check if all night roles are done, if so, call toDay. """
    log("BaseMState __checkToDay",4)
    cop_doc_done = True
    for p in self.players:
      if p.role in ["COP","DOCTOR"] and p.target == None:
        cop_doc_done = False
    
    if (self.__mafia_target == None or not cop_doc_done):
      return False
    else:
      self.__toDay()
      return True

  def __toDay(self):
    """ Change state to day, realizing the mafia's target and all other targets. """
    log("BaseMState __toDay",4)
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
    return True

  def __clearTargets(self):
    """ Clear all player's targets. """
    log("BaseMState __clearTargets",4)
    for p in self.players:
      p.target = None
    self.mafia_target = None

  def __checkWinCond(self):
    """ Check if a team has won, if so end the game. """
    log("BaseMState __checkWinCond",4)
    # Check win conditions
    if self.num_mafia == 0:
      self.comm.cast("TOWN WINS")
      self.comm.cast("TOWN WINS",LOBBY_GROUP_ID)
      self.__endGame()
      return True
    elif self.__num_mafia >= len(self.players)/2:
      self.comm.cast("MAFIA WINS")
      self.comm.cast("MAFIA WINS",LOBBY_GROUP_ID)
      self.__endGame()
      return True
    return False

  def __endGame(self):
    """ Reset State and end the game. """
    log("BaseMState __endGame",4)
    self.day = 0
    self.time = "Day"
    self.players.clear()
    self.comm.clearMafia()

    for winner in self.idiot_winners:
      self.comm.cast(self.comm.getName(winner.id_)+" WON!")
    self.idiot_winners.clear()

    self.comm.cast(self.__revealRoles())
    self.comm.cast(self.__revealRoles(),LOBBY_GROUP_ID)
    return True

  def __revealRoles(self):
    """ Make a string of the original roles that the game started with. """
    log("BaseMState __revealRoles",4)
    r = "GG, here were the roles:"
    for player_id,role in self.savedRoles.items():
      r += "\n" + self.comm.getName(player_id) + ": " + role
    return r

 

  def __addUntil(self, role, weights):
    """ Helper for genRoles """
    log("BaseMState __addUntil",5)
    result = 0
    for i in range(len(weights[0])):
      result += weights[1][i]
      if weights[0][i] == role:
        break
    return result

  def __genRoles(self, num_players):
    """ Create a list of roles of length num_players. Uses random but semi-fair assignment """
    log("BaseMState __genRoles",4)
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

  def __getPlayer(self, p):
    """ p can be player or id, either way returns the player object associated. """
    log("BaseMState __getPlayer",5)
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
  
  def __loadNotes(self):
    """ Loads all notes that were saved """
    log("BaseMState __loadNotes",4)
    try:
      for varName in SAVES:
        self.__dict__[varName] = loadNote(varName)
    except NoteError as e:
      log(e)

  def __watchTimer(self):
    """ Ticks a timer and switches to the next stage when we take too long. """
    log("BaseMState __watchTimer",5)
    lastTime = self.time
    lastDay  = self.day
    while True:
      try:
        currTime = self.time
        currDay  = self.day
        if self.__timerOn:
          if((not currDay == 0) and currTime == lastTime and currDay == lastDay):
            self._imer_value -= 1
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
      except:
        pass

  def __str__(self):
    """ Return the status of the game. """
    log("BaseMState __str__",5)
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
    

class MServer:

  def __init__(self, CommType=GroupyCommTest, MStateType=MState):
    log("BaseMServer init",3)
    self.comm = CommType()
    self.mstate = MStateType(self.comm)

    self.__init_OPS()

  def do_POST(self,post):
    """Process a POST request from bots watching the chats"""
    log("BaseMServer do_POST",3)
    if post['text'][0:len(ACCESS_KW)] == ACCESS_KW:
      words = post['text'][len(ACCESS_KW):].split()
      ops = {}
      if(  post['group_id'] == MAIN_GROUP_ID):  ops = self.__OPS
      elif(post['group_id'] == MAFIA_GROUP_ID): ops = self.__MOPS
      elif(post['group_id'] == LOBBY_GROUP_ID): ops = self.__LOPS
      else:
        log("POST group_id not found: {}".format(post['group_id']))
        return False
      return self.__do_POST_OPS(post,words,ops)

  def do_DM(self,DM):
    """Process a DM from a player"""
    log("BaseMServer do_DM",3)
    assert 'sender_id' in DM, "No sender_id in DM for do_DM"
    assert 'text' in DM, "No text in DM for do_DM"
    if (not DM['sender_id'] == MODERATOR and
        DM['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = DM['text'][len(ACCESS_KW):].split()
      try:
        role = self.mstate.getPlayer(DM['sender_id']).role
      except Exception as e:
        role = ""
      ops = self.__DM_OPS
      if(not len(words) == 0):
        if(role == "DOCTOR" and words[0] in self.__DOC_OPS):
          ops = self.__DOC_OPS
      elif(role == "COP" and words[0] in self.__COP_OPS):
          ops = self.__COP_OPS
      elif(role == "CELEB" and words[0] in self.__CELEB_OPS):
          ops = self.__CELEB_OPS
      if not ops[words[0]](DM,words):
        self.comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
        return False
    self.mstate.saveNotes()
    return True

  #### HELPER FN ####

  def __do_POST_OPS(self,post,words,ops):
    """Process a POST split into words, using a dict of operations"""
    log("BaseMServer __do_POST_OPS",4)
    if (not len(words) == 0 and words[0] in ops):
      if (not ops[words[0]](post,words)):
        log("{} failed".format(words[0]))
        self.comm.cast("{} failed".format(words[0]),post['group_id'])
        return False
    else:
      log("Invalid request: {}".format(post['text']))
      self.comm.cast("Invalid request, (try {}{} for help)".format(ACCESS_KW,HELP_KW),
                post['group_id'])
      return False
    self.mstate.saveNotes()
    return True

  def __init_OPS(self):
    """Create Operations libraries. Called in __init__"""
    # Lobby Options
    self.__LOPS={ HELP_KW   : self.__lobby_help   ,
                  STATUS_KW : self.__lobby_status ,
                  START_KW  : self.__lobby_start  ,
                  IN_KW     : self.__lobby_in     ,
                  OUT_KW    : self.__lobby_out    ,
                  WATCH_KW  : self.__lobby_watch  ,
                }

    # Main OPS
    self.__OPS ={ VOTE_KW   : self.__vote   ,
                  STATUS_KW : self.__status ,
                  HELP_KW   : self.__help   ,
                  TIMER_KW  : self.__timer  ,
                }

    # Mafia OPS
    self.__MOPS={ HELP_KW   : self.__mafia_help    ,
                  TARGET_KW : self.__mafia_target  ,
                  OPTS_KW   : self.__mafia_options ,
                }

    self.__DOC_OPS = { HELP_KW    : self.__doc_help ,
                       OPTS_KW    : self.__doc_options ,
                       TARGET_KW  : self.__doc_save ,
                     }
    self.__COP_OPS = { HELP_KW    : self.__cop_help ,
                       OPTS_KW    : self.__cop_options ,
                       TARGET_KW  : self.__cop_investigate ,
                     }
    self.__CELEB_OPS={ HELP_KW    : self.__celeb_help,
                       REVEAL_KW  : self.__celeb_reveal,
                     }
    self.__DM_OPS =  { HELP_KW    : self.__dm_help,
                       STATUS_KW  : self.__dm_status,
                     }

  ### LOBBY GROUP FN -----------------------------------------------------------

  def __lobby_help(self,post={},words=[]):
    log("BaseMServer __lobby_help",5)
    self.comm.cast(L_HELP_MESSAGE,LOBBY_GROUP_ID)
    return True

  def __lobby_status(self,post={},words=[]):
    log("BaseMServer __lobby_status",5)
    self.comm.cast(mstate.__str__(),LOBBY_GROUP_ID)
    return True

  def __lobby_start(self,post={},words=[]):
    log("BaseMServer __lobby_start",5)
    # NOTE: When the day is 0, the following is true:
    if self.mstate.day == 0:
      return self.mstate.startGame()
    else:
      self.comm.cast("A game is already in progress. Watch with {}{}".format(ACCESS_KW,WATCH_KW),
                     LOBBY_GROUP_ID)
      return True

  def __lobby_in(self,post,words=[]):
    log("BaseMServer __lobby_in",5)
    assert 'user_id' in post, "No user_id in __lobby_in post"
    # Get player to go in
    player_id = post['user_id']
    # Add to next list
    return self.mstate.inNext(player_id)

  def __lobby_out(self,post,words=[]):
    log("BaseMServer __lobby_out",5)
    assert 'user_id' in post, "No user_id in __lobby_out post"
    player_id = post['user_id']
    # try to remove from list:
    if player in self.mstate.nextPlayerIDs:
      self.mstate.nextPlayerIDs.remove(player)
      self.comm.cast("{} removed from next game".format(self.comm.getName(player)),
                     LOBBY_GROUP_ID)
    else:
      self.comm.cast("{} wasn't in the next game".format(self.comm.getName(player)),
                     LOBBY_GROUP_ID)
    return True

  def __lobby_watch(self,post,words=[]):
    log("BaseMServer __lobby_watch",5)
    if self.mstate.day == 0:
      self.comm.cast("No game to watch",LOBBY_GROUP_ID)
      return True
    assert 'user_id' in post, "No user_id in __lobby_watch post"
    player_id = post['user_id']
    # if they aren't already in the game, add to game
    return self.comm.addMain(player_id)

  ### MAIN GROUP FN ------------------------------------------------------------

  def __vote(self,post,words):
    log("BaseMServer __vote",5)
    assert 'user_id' in post, "No user_id in __vote post"
    voter = post['user_id']

    if words[1].lower() == "me":
      votee = voter
    elif words[1].lower() == "none":
      votee = None
    elif words[1].lower() == "nokill":
      votee = "0"
    elif ('attachments' in post and
        len([a for a in post['attachments'] if a['type'] == 'mentions']) >= 1):
      assert 'user_ids' in mentions[0] and len(mentions[0]['user_ids']) >= 1, "No user_ids in mention in _vote post"
      votee = mentions[0]['user_ids'][0]
    else:
      self.log("Vote Failed: couldn't get votee")
      return False
    return self.mstate.vote(voter,votee)

  def __status(self,post={},words=[]):
    log("BaseMServer __status",5)
    self.comm.cast(mstate.__str__())
    return True

  def __help(self,post={},words=[]):
    log("BaseMServer __help",5)
    self.comm.cast(HELP_MESSAGE)
    return True

  def __timer(self,post={},words=[]):
    log("BaseMServer __timer",5)
    return self.mstate.setTimer()

  ### MAFIA GROUP FN -----------------------------------------------------------

  def __mafia_help(self,post={},words=[]):
    log("BaseMServer __mafia_help",5)
    self.comm.cast(M_HELP_MESSAGE,MAFIA_GROUP_ID)
    return True

  def __mafia_target(self,post,words):
    log("BaseMServer __mafia_target",5)
    try:
      return self.mstate.mafiaTarget(int(words[1]))
    except Exception as e:
      log("Invalid Mafia Target {}".format(e))
      return False


  def __mafia_options(self,post={},words=[]):
    log("BaseMServer __mafia_options",5)
    return self.mstate.mafia_options()

  ### DOC DM FN ----------------------------------------------------------------

  def __doc_help(self,DM,words=[]):
    log("BaseMServer __doc_help",5)
    self.comm.sendDM(DOC_HELP_MESSAGE, DM['sender_id'])
    return True

  def __doc_save(self,DM,words):
    log("BaseMServer __doc_save",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Doctor save failed: {}".format(e))
    return False

  def __doc_options(self,DM,words=[]):
    log("BaseMServer __doc_options",5)
    return self.mstate.send_options("Use /target number (i.e. /target 0) to pick someone to save",
                                    DM['sender_id'])

  ### COP DM FN ----------------------------------------------------------------

  def __cop_help(self,DM,words=[]):
    log("BaseMServer __cop_help",5)
    self.comm.sendDM(COP_HELP_MESSAGE, DM["sender_id"])
    return True

  def __cop_investigate(self,DM,words):
    log("BaseMServer __cop_investigate",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Cop investigation failed: {}".format(e))
    return False

  def __cop_options(Self,DM,words=[]):
    log("BaseMServer __cop_options",5)
    return self.mstate.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",
                                    DM['sender_id'])

  ### CELEB DM FN --------------------------------------------------------------

  def __celeb_help(self,DM,words=[]):
    log("BaseMServer __celeb_help",5)
    self.comm.sendDM(CELEB_HELP_MESSAGE, DM["sender_id"])
    return True

  def __celeb_reveal(self,DM,words=[]):
    log("BaseMServer __celeb_reveal",5)
    return self.mstate.reveal(DM["sender_id"])

  ### DM FN --------------------------------------------------------------------

  def __dm_help(self,DM,words):
    log("BaseMServer __dm_help",5)
    return self.comm.sendDM(DM_HELP_MESSAGE,DM['sender_id'])

  def __dm_status(self,DM,words=[]):
    log("BaseMServer __dm_status",5)
    return self.comm.sendDM(mstate.__str__(),DM['sender_id'])


def makePost(group_id,text,user_id="",mentions=[]):
  post = {}
  post['group_id'] = group_id
  post['text'] = text
  post['user_id'] = user_id
  post['attachments'] = [{'type':'mentions','user_ids':mention} for mention in mentions]
  return post

def makeDM(sender_id,text):
  DM = {}
  DM['sender_id'] = sender_id
  DM['text'] = text
  return DM
