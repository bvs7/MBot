from MInfo import *
from MTimer import MTimer


class GameOverException(Exception):
  def __init__(self, lobby_id):
    self.lobby_id = lobby_id

class MPlayer:
  
  def __init__(self, id, role, name=None):
    self.id = id
    self.role = role
    self.name = name
    self.vote = None
    self.target = None
		
    self.timered = False
    
  def __str__(self):
    return "{}({})".format(self.id, self.role)
    

class MState:

  def __init__(self, id, mainComm, mafiaComm, lobbyComm, rules, roles, rec, MTimerClass=MTimer):
    
    self.id = id
    self.mainComm = mainComm
    self.mafiaComm = mafiaComm
    self.lobbyComm = lobbyComm
    self.rules = rules # TODO let this be default (None)
    self.rec = rec
    self.MTimerClass=MTimerClass
    
    # Generate initial state
    self.day = 0
    self.phase = "Init"
    self.players = []
    self.num_mafia = 0
    
    self.savedRoles = roles
    self.mafiaTarget = None
    self.blocked_ids = []
    
    self.timer = None
    
    self.null = MPlayer("0", "_", "_")

    self.idiot_winners = []
    
    
    # Initialize players
    for p_id, role in roles.items():
      name = self.lobbyComm.getName(p_id)
      self.players += [MPlayer(p_id, role, name)]
      if role in MAFIA_ROLES:
        self.num_mafia += 1
        
    self.players.sort(key=(lambda player:player.name))
    # Log the creation of this game
    self.rec.create(self.id, self.players, self.__roleDict(roles.values()))
    
  def start_game(self):
    
    # Add all players
    for player in self.players:
      self.mainComm.add(player.id, player.name)
      if player.role in MAFIA_ROLES:
        self.mafiaComm.add(player.id, None)
      self.mainComm.send(GIVE_ROLE.format(player.role),player.id)
        
    self.day = 1
    self.phase = "Day"
    # Starting messages
    
    msg = START_GAME_MESSAGE_MAIN + '\n'.join([p.name for p in self.players])
      
    if "known_roles" in self.rules:
      if self.__testRules("known_roles") == "ON":
        msg += "\nThe Roles:" + self.__showRoles()
      elif self.__testRules("known_roles") == "TEAM":
        msg += "\nThe Teams:" + self.__showTeams()
        
    self.mainComm.cast(msg)
    
    mafList = [p for p in self.players if p.role in MAFIA_ROLES] #.sort(key=(lambda x:x.name))
    strList = ["{}:{}".format(p.name,p.role) for p in mafList]
    
    msg = START_GAME_MESSAGE_MAFIA + '\n'.join(strList)
    
    self.mafiaComm.cast(msg)
    
    self.rec.start()
    
    if (self.__testRules("start_night") == "ON" or 
       (self.__testRules("start_night") == "EVEN" and len(self.players)%2==0) ):
       self.__toNight()
       
       
  def vote(self, voter_id, votee_id):
    if not self.phase == "Day":
      self.mainComm.cast(ONLY_VOTE_DAY)
      return
      
    try:
      voter = self.getPlayer(voter_id)
    except Exception as e: # TODO: replace with custom exception?
      self.mainComm.cast("Error processing vote: Bad voter id: {}".format(e))
      return
      
    if votee_id == None:
      votee = None
    elif votee_id == "0":
      votee = self.null
    else:
      try:
        votee = self.getPlayer(votee_id)
      except Exception as e: # TODO: replace with custom exception?
        self.mainComm.cast("Error processing vote: Bad votee id")
        return
    
    if voter.vote == votee:
      self.mainComm.cast(SAME_VOTE.format(voter.name))
      return
    voter.vote = votee
    
    self.rec.vote(int(voter_id), None if votee_id==None else int(votee_id), self.day)
    
    self.__checkVotes(votee)
    
  def mafia_target(self, p_id, target_option):
    """ Change Mafia's target to players[target_option] """
    if not self.phase == "Night":
      self.mafiaComm.cast(ONLY_TARGET_NIGHT)
      return
    
    if target_option == None:
      return

    target_number = ord(target_option)-ord('A')
    if target_number == len(self.players):
      target = self.null
    elif target_number == None:
      target = None
    else:
      target = self.players[target_number]

    self.mafiaTarget = target
    self.mafiaComm.cast(TARGET_SUCCESSFUL.format(target_option))

    self.rec.mafia_target(int(p_id),int(target.id),self.day)

    self.__checkToDay()
    
  def mafia_options(self):
    """ Send the mafia's options to the mafia chat. """
    if self.phase != "Night":
      return
    msg = MAFIA_TARGET_PROMPT
    c = 'A'
    for player in self.players:
      msg += "\n"+c+" "+player.name
      c = chr(ord(c)+1)
    msg += "\n"+c+" No kill"
    self.mafiaComm.cast(msg)
		
  def target(self, p_id, target_option):
    """ Change p's target to players[target_option]. """
    try:
      player = self.getPlayer(p_id)
    except Exception:
      return
			
    if not self.phase == "Night":
      self.mainComm.send(ONLY_TARGET_NIGHT,player.id)
      return

    target_number = ord(target_option)-ord('A')
    if target_number == len(self.players):
      target = self.null
    elif target_number == None:
      target = None
    else:
      target = self.players[target_number]
			
    if player.role == "MILKY" and target == player:
      self.mainComm.send(MILK_SELF_RESPONSE, player.id)
      return
	
    player.target = target
    self.mainComm.send(TARGET_SUCCESSFUL.format(target_option),player.name)

    self.rec.target(int(player.id), int(target.id), self.day)

    self.__checkToDay()
	
  def send_options(self,p_id,prompt=None):
    """ Send list of options to player p with preface prompt. """
    try:
      p = self.getPlayer(p_id)
    except Exception as e:
      # TODO Error message/recovery?
      return
    if prompt == None:
      if p.role == "COP":
        prompt = ("Use /target letter (i.e. /target C) "
                 "to pick someone to investigate")
      elif p.role == "DOCTOR":
        prompt = ("Use /target letter (i.e. /target D) "
                 "to pick someone to save")
      elif p.role == "STRIPPER":
        prompt = ("Use /target letter (i.e. /target A) "
                 "to pick someone to distract")
      elif p.role == "MILKY":
        prompt = ("Use /target letter (i.e. /target B) "
                 "to pick someone to milk")
    if prompt == None:
      return # TODO: make sure options aren't sent if no need to target
    msg = prompt
    c = 'A'
    for player in self.players:
      msg += "\n"+c+" "+player.name
      c = chr(ord(c)+1)
    msg += "\n"+c+" No target"
    self.mainComm.send(msg,p.id)
      
  def try_reveal(self, p_id):
    """Attempt to reveal. If not a CELEB or it's night or CELEB was stripped, fail"""
    try:
      player = self.getPlayer(p_id)
    except Exception as e:
      # TODO Error logging
      return

    if player.role == "CELEB":
      if not self.phase == "Day":
        self.mainComm.send("Must reveal during Day",player.id)
        return
      if not player.id in self.blocked_ids:
        self.rec.reveal(int(player.id), self.day, False)
        self.reveal(player.id)
      else:
        self.mainComm.send("You were distracted",player.id)
        self.rec.reveal(int(player.id), self.day, True)
    else:
      self.mainComm.send("Only CELEB can reveal themselves.",player.id)
      return

  def reveal(self,p):
    """ Reveal a player's role to the Main Chat """
    try:
      player = self.getPlayer(p)
    except Exception as e:
      # TODO Error Logging
      return
    self.mainComm.cast(player.name + " is " + player.role)
		
  def revealTeam(self,p):
    """ Reveal a player's team to the Main Chat """
    try:
      player = self.getPlayer(p)
    except Exception as e:
      # Error Logging
      return
    if player.role in MAFIA_ROLES:
      team = "Mafia"
    elif player.role in TOWN_ROLES:
      team = "Town"
    elif player.role in ROGUE_ROLES:
      team = "Rogue"
    self.mainComm.cast(player.name + " is aligned with " + team)
    return
      
  def getPlayer(self, p):
    """ p can be player or id, either way returns the player object associated. """  
    if type(p) == MPlayer:
      return p
    elif type(p) == str:
      players = [player for player in self.players if player.id == p]
      if len(players) >= 1:
        return players[0]
      else:
        raise Exception("Couldn't find player from id {}".format(p)) # TODO: make an appropriate exception
    else:
      raise Exception("Couldn't find player from {}".format(p))
			
  def setTimer(self, player_id):
    """ Start an N * 5 minute timer where N is number of players, or reduce timer by 5 minutes """
    try:
      player = self.getPlayer(player_id)
    except Exception as e:
      # Error logging
      return

    if player.timered:
      self.mainComm.cast("You have already timered.")
      return
			
    if self.timer == None:
      player.timered = True
      self.timer = self.__standard_timer()
      self.mainComm.cast("Timer started: {}".format(self.timer))
    else:
      player.timered = True
      self.timer.addTime(-SET_TIMER_VALUE)
      self.mainComm.cast("Timer reduced: {}".format(self.timer))

  def unSetTimer(self, player_id):
    try:
      player = self.getPlayer(player_id)
    except Exception as e:
      # Error logging
      return

    if not player.timered:
      self.mainComm.cast("You haven't timered.")
      return
    
    player.timered = False
    if len([p for p in self.players if p.timered]) == 0:
      self.timer.halt()
      self.timer = None
      self.mainComm.cast("Timer halted.")
    else:
      self.timer.addTime(SET_TIMER_VALUE)
      self.mainComm.cast("Timer extended: {}".format(self.timer))

  def tryLeaveMain(self, player_id):
    if player_id in [p.id for p in self.players]:
      self.mainComm.cast("You can't leave, aren't you playing?")
    else:
      self.mainComm.remove(player_id)

  def tryLeaveMafia(self, player_id):
    if player_id in [p.id for p in self.players]:
      self.mafiaComm.cast("You can't leave, aren't you playing?")
    else:
      self.mafiaComm.remove(player_id)

  def __standard_timer(self, value=None):
    if value == None:
      time = len(self.players) * SET_TIMER_VALUE
    else:
      time = value
    alarms = {
      0:[self.__progress_phase],
      20:[self.__warning],
      60:[self.__warning],
      5*60:[self.__warning],
      10*60:[self.__warning],
      15*60:[self.__warning]
    }
    return self.MTimerClass(time, alarms, self.id)

  def __progress_phase(self):
    if self.phase == "Day":
      self.__toNight()
    elif self.phase == "Night":
      self.__toDay()

  def __warning(self):
    if self.timer == None:
      return
    if self.timer.value == 15 * 60:
      self.mainComm.cast("Fifteen minutes remaining")
    if self.timer.value == 10 * 60:
      self.mainComm.cast("Ten minutes remaining")
    elif self.timer.value == 5 * 60:
      self.mainComm.cast("Five minutes remaining (tick tock, bish)")
    elif self.timer.value == 60:
      self.mainComm.cast("One minute remaining, one minute")
    elif self.timer.value == 20:
      self.mainComm.cast("Twenty Seconds")

  def __checkVotes(self, player):
    if player == None:
      self.mainComm.cast("Vote retracted")
      return
    
    voters = [v for v in self.players if v.vote == player]
    voter_ids = [int(v.id) for v in voters]
    num_voters = len(voters)
    num_players = len(self.players)

    if player == self.null:
      if num_voters < num_players/2:
        need = int((num_players+1)/2) - num_voters
        msg = "Vote successful: {} more vote{}to decide not to kill"
        self.mainComm.cast(msg.format(need, " " if need == 1 else "s "))
      else:
        self.mainComm.cast("You have decided not to kill anyone")
        self.rec.elect(voter_ids, int(player.id), self.day, self.__roleDict())
        self.__toNight()
    elif num_voters > num_players/2:
      self.mainComm.cast(
        "The vote to kill {} has passed".format(player.name))
      self.__kill(player, voter_ids, "elect")
      self.__toNight()

    else:
      need = int((num_players)/2+1)-num_voters
      msg = "Vote successful: {} more vote{}until {} is killed"
      self.mainComm.cast(msg.format(need, " " if need == 1 else "s ",
        player.name))

  def __kill(self, player, guilty_ids, kill_type):
    if player.role in MAFIA_ROLES:
      self.num_mafia -= 1
    self.players.remove(player)

    if kill_type == "elect":
      self.rec.elect(guilty_ids, int(player.id), self.day, self.__roleDict())
    elif kill_type == "murder":
      self.rec.murder(guilty_ids, int(player.id), self.day, True, self.__roleDict())


    if player.role == "IDIOT":
      ## TODO: IDIOT win rules!!!
      if self.__testRules("reveal_on_death") == "ON":
        self.mainComm.cast("{} WON!".format(player.name))
        self.idiot_winners.append(player)

    self.__checkWinCond()

    self.mainComm.send("You died... here were the roles:" + self.__revealRoles(), player.id)

    if self.__testRules("reveal_on_death") == "ON":
      self.reveal(player)
    elif self.__testRules("reveal_on_death") == "TEAM":
      self.revealTeam(player)

  def __checkToDay(self):
    for player in self.players:
      if player.role in TARGET_ROLES and player.target == None:
        return 
    # All target roles are done
    if self.mafiaTarget == None:
      return
    # Mafia also done
    self.__toDay()

  def __toDay(self):
    self.__haltTimer()
    self.mainComm.cast("Uncertainty dawns, as does this day.")

    self.rec.day()
    self.__resolveStripperActions()
    self.__resolveMafiaKill()
    self.__resolveMilkyGift()
    self.__resolveCopInvestigation()
    self.__clearTargets()
    
    self.phase = "Day"
    self.day += 1

  def __resolveStripperActions(self):
    self.blocked_ids = []
    for s in [p for p in self.players if p.role == "STRIPPER"]:
      if s.target != None and not s.target.id in self.blocked_ids:
        self.blocked_ids.append(s.target.id)

  def __resolveMafiaKill(self):
    if not self.mafiaTarget in [None, self.null]:
      saviors = []
      for doctor in self.players:
        if ((doctor.role == "DOCTOR") and (not doctor.target == None) and
            (doctor.target == self.mafiaTarget)):
          if not doctor.id in self.blocked_ids:
            saviors.append(doctor)
          else:
            self.mainComm.send("You were distracted",doctor.id)

      maf_ids = [int(m.id) for m in self.players if m.role in MAFIA_ROLES]

      if saviors:
        self.rec.murder(maf_ids, int(self.mafiaTarget.id), self.day, False, self.__roleDict())
        if "SELF" in self.__testRules("know_if_saved"):
          self.mainComm.send("You were saved!", self.mafiaTarget.id)
        for savior in saviors:
          if "DOC" in self.__testRules("know_if_saved"):
            self.mainComm.send("Your save was successful!", savior.id)
        return
      else:
        msg = "Tragedy has struck! {} is dead!".format(self.mafiaTarget.name)
        self.mainComm.cast(msg)
        self.__kill(self.mafiaTarget, maf_ids, "murder")

  def __resolveMilkyGift(self):
    for milky in self.players:
      if (milky.role == "MILKY" and (not milky.target in [None, self.null]) and
        milky.target in self.players):
        if not milky.id in self.blocked_ids:
          ### TODO: Create MILK
          self.mainComm.cast("{} received milk!".format(milky.target.name))
        else:
          self.mainComm.send("You were distracted", milky.id)

  def __resolveCopInvestigation(self):
    for cop in self.players:
      if cop.role == "COP" and (not cop.target in [None, self.null]):
        if not cop.id in self.blocked_ids:
          if cop.target.role == "MILLER" or (cop.target.role in MAFIA_ROLES
            and not cop.target.role == "GODFATHER"):
            team = "Mafia"
          else:
            team = "NOT Mafia"
          self.mainComm.send("{} is {}".format(cop.target.name, team), cop.id)
        else: # Cop was blocked
          self.mainComm.send("You were distracted", cop.id)

  def __clearTargets(self):
    for player in self.players:
      player.target = None
    self.mafiaTarget = None

  def __toNight(self):
    self.__haltTimer()
    self.phase = "Night"
    self.rec.night()
    for player in self.players:
      player.vote = None

    self.mainComm.cast("Night falls and everyone sleeps")
    self.mafiaComm.cast("As the sky darkens, so too do your intentions. "
                        "Pick someone to kill")

    self.mafia_options()
    for p in self.players:
      if p.role == "COP":
        self.send_options(p.id,"Use /target letter (i.e. /target C) "
                          "to pick someone to investigate")
      elif p.role == "DOCTOR":
        self.send_options(p.id,"Use /target letter (i.e. /target D) "
                          "to pick someone to save")
      elif p.role == "STRIPPER":
        self.send_options(p.id,"Use /target letter (i.e. /target A) "
                          "to pick someone to distract")
      elif p.role == "MILKY":
        self.send_options(p.id,"Use /target letter (i.e. /target B) "
                          "to pick someone to milk")

    if "NIGHT" in self.__testRules("auto_timer"):
      self.timer = self.__standard_timer(5*60)
      for player in self.players:
        player.timered = True
      self.mainComm.cast("Timer started: {}".format(self.timer))

  def __testRules(self, rule):
    return self.rules.get(rule, "OFF")

  def __haltTimer(self):
    if not self.timer == None and self.timer.active:
      self.timer.halt()
    self.timer = None
    for player in self.players:
      player.timered = False

  def __checkWinCond(self):
    if self.num_mafia == 0:
      self.mainComm.cast("Town WINS")
      self.lobbyComm.cast("Town WINS")
      self.rec.end("Town",self.phase, self.day)
    elif self.num_mafia >= len(self.players)/2:
      self.mainComm.cast("Mafia WINS")
      self.lobbyComm.cast("Mafia WINS")
      self.rec.end("Mafia",self.phase, self.day)
    else:
      return
    self.lobbyComm.cast(self.__revealRoles())
    self.__endGame()

  def __endGame(self):
    for winner in self.idiot_winners:
      self.mainComm.cast("{} WON!".format(winner.name))

    self.rec.archive()

    self.lobbyComm.cast("GG, here were the roles:" + self.__revealRoles())

    raise GameOverException(self.lobbyComm.id)

  def __revealRoles(self):
    """ Make a string of the original roles that the game started with. """
    r = ""

    savedRolesSortedIDs = sorted(self.savedRoles, key=(lambda x: ALL_ROLES.index(self.savedRoles[x])))
  
    for player_id in savedRolesSortedIDs:
      role = self.savedRoles[player_id]
      r += "\n" + self.lobbyComm.getName(player_id) + ": " + role
    return r

  def __getCurrentRoles(self):
    roles = []
    for player in self.players:
      roles.append(player.role)
    return roles

  def __roleDict(self,roles=None):
    """Generate roleDict from roles"""
    if roles == None:
      roles = self.__getCurrentRoles()
    roleDict = {}
    for role in roles:
      if role in roleDict:
        roleDict[role] += 1
      else:
        roleDict[role] = 1
    return roleDict

  def __showRoles(self,roles=None):
    roleDict = self.__roleDict(roles)
    msg = ""
    for role in ALL_ROLES:
      if role in roleDict and roleDict[role] > 0:
        msg += "\n" + role + ": " + str(roleDict[role])
    return msg

  def __showTeams(self,roles=None):
    if roles == None:
      roles = self.__getCurrentRoles()
    teamDict = {"Mafia":0, "Town":0}
    for role in roles:
      if role in MAFIA_ROLES:
        teamDict["Mafia"] += 1
      elif role in TOWN_ROLES:
        teamDict["Town"] += 1
      elif role == ROGUE_ROLES:
        if not "Rogue" in teamDict:
            teamDict["Rogue"] = 0
        teamDict["Rogue"] += 1

    msg = ""
    for key in TEAMS:
      if key in teamDict:
        msg += "\n" + key + ": " + str(teamDict[key])
    return msg 	

  def __str__(self):
    m = "GAME #{}: {} {}: ".format(self.id,self.phase,self.day)
    if not self.timer == None:
      m += str(self.timer)
    m += "\n"
    for player in self.players:
      if player.timered:
          m += "[t!] "
      m += player.name + " : "
      count = 0
      for voter in [v for v in self.players if v.vote == player]:
          count += 1
          m += voter.name + ", "
      m += str(count) + "\n"

    if self.__testRules("known_roles") == "ON" and self.__testRules("reveal_on_death") == "ON":
      m += self.__showRoles([p.role for p in self.players])
    elif self.__testRules("known_roles") in ("ON","TEAM") and self.__testRules("reveal_on_death") in ("ON","TEAM"):
      m += self.__showTeams([p.role for p in self.players])
    else:
      roles = []
      for r in self.savedRoles.values():
        roles.append(r)
      if self.__testRules("known_roles") == "ON":
        m += "\nOriginal Roles:" + self.__showRoles([self.savedRoles.values()])
      elif self.__testRules("known_roles") == "TEAM":
        m += "\nOriginal Teams:" + self.__showTeams([self.savedRoles.values()])

    return m
