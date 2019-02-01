from MInfo import *
from MTimer import MTimer
from MState import MState, GameOverException
from MComm import MComm, GroupComm
from MRecord import MRecord
from DBMRecord import DBMRecord

import time


class LobbyComm:

  """
  Lobby has all the interfaces of its CommType.
  It also includes all of the state of a lobby
  """

  def __init__(self, lobby_id, CommType, TimerType):
    CommType.__init__(self, lobby_id) # Initialize lobbyComm, then add extras

    self.TimerType = TimerType
    self.start_timer = None
    self.start_message_ids = []
    self.minplayers = 3
    
    self.rules = self.__load_rules()
    self.mstate = None 

  def __str__(self):
    if self.mstate = None:
      if self.start_timer != None:
        seconds = self.start_timer.getTime()
        return ("Game will start in {}:{:0>2d} (at {}). "
                "If there are at least {} players)").format(
                  seconds//60, seconds%60,
                  time.strftime("%I:%M",time.localtime(time.time() + (seconds))),
                  self.minplayers )
      else:
        return "No games"
    else:
      return str(self.mstate)

class MController:

  def __init__(self, lobby_ids, group_ids, CommType=GroupComm, RecordType=DBMRecord, TimerType=MTimer):

    self.CommType = CommType
    self.RecordType = RecordType
    self.TimerType = TimerType

    self.lobbyComms = {} # mapping from lobby_id to lobby
    for lobby_id in lobby_ids:
      comm = LobbyComm(lobby_id, CommType, TimerType)
      self.lobbyComm[lobby_id] = comm

    self.determined_roles = []

    self.availableComms = []
    for group_id in group_ids:
      comm = CommType(group_id)
      self.availableComms.append(comm)

  def __getGroupType(self, group_id, sender_id):
    """ Looking for group_type name, detail (extra data to send to command
      and respond, func that takes msg to respond generically """
    # Get group type
    group_type = ""
    if group_id in self.lobbyComms:
      lobby = self.lobbyComms[group_id]
      return ("lobby", lobby, lobby.cast)
    mainComms = [(l.mstate.mainComm.id, l.mstate) for l in self.lobbyComms if l.mstate.mainComm.id == group_id]
    if len(mainComms) == 1:
      mstate = mainComms[0][1]
      return ("main", mstate, mstate.mainComm.cast)
    mafiaComms = [(l.mstate.mafiaComm.id, l.mstate) for l in self.lobbyComms if l.mstate.mafiaComm.id == group_id]
    if len(mafiaComms) == 1:
      mstate = mafiaComms[0][1]
      return ("mafia", mstate, mstate.mafiaComm.cast)
    elif '+' in group_id:
      return ("DM", None, lambda msg : self.CommType.static_send(msg, sender_id))
    elif group_id in [a.id for a in self.availableComms]:
      for availComm in self.availableComms:
        if availComm.id == group_id:
          return ("avail", availComm, availComm.cast)

  def command(self, keyword, group_id, message_id, sender_id, data): # TODO: just data? it includes all ids
    """ If this is a DM, group id has a '+' in it, sender_id is sender
    
    Command | Lobby | Main | Mafia | DM | Avail
    start   |   X   |      |       |    |
    extend  |   X   |      |       |    |
    in      |   X   |      |       |    |
    out     |   X   |      |       |    |
    watch   |   X   |      |       |    |
    vote    |       |  X   |       |    |
    timer   |       |  X   |       |    |
    untimer |       |  X   |       |    |
    target  |       |      |   X   |  X |
    reveal  |       |      |       |  X |
    status  |   X   |  X   |   X   |  X |
    stats   |   X   |      |       |  X |
    rule    |   X   |  X   |   X   |    |
    leave   |   X   |  X   |   X   |    |  X
    help    |   X   |  X   |   X   |  X |
    """

    # Get group type
    (group_type, detail, respond) = self.__getGroupType(group_id, sender_id)
      
    cmd_name = keyword + '_' + group_type + '_command'
    if not hasattr(self, cmd_name):
      respond('Invalid keyword "{}" for {} chat'.format(keyword, group_type))
      return
    method = getattr(self, cmd_name)

    try:
      method(detail, group_id, message_id, sender_id, data)
    except GameOverException as goe:
      # Using goe.lobby, reset lobby's mstate
      self.availableComms.append(goe.lobby.mstate.mafiaComm)
      self.availableComms.append(goe.lobby.mstate.mainComm)
      goe.lobby.mstate = None

  def __parse_start(words):
    minutes = 1
    minplayers = 3
    try:
      if len(words) >= 3:
        minplayers = int(words[2])
      if len(words) >= 2:
        minutes = int(words[1])
    except ValueError as e:
      pass
    return (minutes, minplayers)

  def start_lobby_command(self, lobby, message_id, member_id, data):
    # Stop timer if there is one now
    if not lobby.start_timer == None:
      lobby.start_timer.halt()

    (minutes, lobby.minplayers) = __parse_start(data['text'].split())

    seconds = minutes * 60
    msg = str(lobby) + " Like this to join"

    lobby.start_message_ids.append(lobby.cast(msg))
    alarms = {
      0 : [lambda : self.__start_game(lobby)],
    }
    lobby.start_timer = lobby.TimerType(minutes*60, alarms)

  def __parse_extend(words):
    minutes = 1
    try:
      if len(words) >= 2:
        minutes = int(words[1])
    except ValueError as e:
      pass
    return minutes

  def extend_lobby_command(self, lobby, message_id, member_id, data):
     if lobby.start_timer == None:
      lobby.cast("No game is starting")
      return
    minutes = __parse_extend(words)

    lobby.start_timer.addTime(minutes*60)
    if lobby.start_timer.getTime() > 10: # If it isn't immediately starting... TODO: magic number
      msg = str(lobby) + " You can also like this message to join."
      lobby.start_message_ids.append(lobby.cast(msg))

  def in_lobby_command(self, lobby, message_id, member_id, data):
    lobby.cast("Unfortunately, /in doesn't work right now")

  def out_lobby_command(self, lobby, message_id, member_id, data):
    lobby.cast("Unfortunately, /out doesn't work right now")

  def watch_lobby_command(self, lobby, message_id, member_id, data):
    lobby.ack(message_id)
    if lobby.mstate == None:
      lobby.cast("No game to watch")
      return
    lobby.mstate.mainComm.add(member_id, lobby.getName(member_id))

  def status_lobby_command(self, lobby, message_id, member_id, data):
    lobby.cast(str(lobby))

  def stats_lobby_command(self, lobby, message_id, member_id, data):
    lobby.ack(message_id)
    msg = CALLBACK_URL + ":" + STATS_PORT
    lobby.cast(msg)

  def rule_lobby_command(self, lobby, message_id, member_id, data):
    #TODO: Implement rules
    lobby.cast("Unfortunately, rules cannot be changed for now")

  def help_lobby_command(self, lobby, message_id, member_id, data):
    #TODO: Implement help
    lobby.cast("Unfortunately, help isn't available for now")


  @staticmethod
  def __parse_votee(voter_id, data):
    words = data['text'].split()
    if len(words) < 2:
      return None
    elif words[1].lower() == "me":
      return voter_id
    elif words[1].lower() == "nokill":
      return "0"
    elif 'attachments' in data:
      mentions = [a for a in data['attachments'] if a['type'] == 'mention']
      if (len(mentions) > 0 and 
          'user_ids' in mentions[0] and 
          len(mentions[0]['user_ids']) >= 1):
        return mentions[0]['user_ids'][0]

  def vote_main_command(self, mstate, message_id, member_id, data):
    votee_id = __parse_votee(member_id, data)
    mstate.mainComm.ack(message_id)
    mstate.vote(member_id, votee_id)

  def timer_main_command(self, mstate, message_id, member_id, data):
    mstate.setTimer(member_id)

  def untimer_main_command(self, mstate, message_id, member_id, data):
    mstate.unSetTimer(member_id)

  def status_main_command(self, mstate, message_id, member_id, data):
    mstate.cast(str(mstate))

  def rule_main_command(self, mstate, message_id, member_id, data):
    mstate.mainComm.cast("Unfortunately, rules cannot be changed for now")

  def leave_main_command(self, mstate, message_id, member_id, data):
    mstate.tryLeaveMain(member_id)

  def help_main_command(self, mstate, message_id, member_id, data):
    mstate.mainComm.cast("Unfortunately, help isn't available for now")


  @staticmethod
  def __parse_target(mstate, words):
    if len(words) >= 2:
      if len(words[1]) == 1:
        return words[1]

  def target_mafia_command(self, mstate, message_id, member_id, data):
    target_option = __parse_target(data['text'].split())
    if target_option == None:
      mstate.mafiaComm.cast("Invalid target")
    else:
      mstate.mafia_target(member_id, target_option)

  def status_mafia_command(self, mstate, message_id, member_id, data):
    mstate.mafiaComm.cast(str(mstate))
    mstate.mafia_options()

  def rule_mafia_command(self, mstate, message_id, member_id, data):
    mstate.mafiaComm.cast("Unfortunately, rules cannot be changed for now")

  def leave_mafia_command(self, mstate, message_id, member_id, data):
    mstate.tryLeaveMafia(member_id)

  def help_mafia_command(self, mstate, message_id, member_id, data):
    mstate.mafiaComm.cast("Unfortunately, help isn't available for now")


  def target_DM_command(self, DM, message_id, member_id, data):
    # TODO: Determine which game this is for
    # Temp, if only one lobby
    if len(self.lobbyComms) == 1:
      mstate = self.lobbyComms[0].mstate

    target_option = __parse_target(data['text'].split())
    if target_option == None:
      self.CommType.static_send("Invalid target", member_id)
    else:
      mstate.target(member_id, target_options)
    
  def reveal_DM_command(self, DM, message_id, member_id, data):
    # TODO: Determine which game this is for
    # Temp, if only one lobby
    if len(self.lobbyComms) == 1:
      mstate = self.lobbyComms[0].mstate
    mstate.try_reveal(member_id)

  def status_DM_command(self, DM, message_id, member_id, data):
    # TODO: Determine which game this is for
    # Temp, if only one lobby
    if len(self.lobbyComms) == 1:
      mstate = self.lobbyComms[0].mstate
    self.CommType.static_send(str(mstate), member_id)
    mstate.send_options(member_id)

  def stats_DM_command(self, DM, message_id, member_id, data):
    msg = CALLBACK_URL + ":" + STATS_PORT
    self.CommType.static_send(msg, member_id)

  def help_DM_command(self, DM, message_id, member_id, data):
    self.CommType.static_send("Unfortunately, help isn't available for now", member_id)

  def leave_avail_command(self, avail, message_id, member_id, data):
    avail.remove(member_id)

  def help_avail_command(self, avail, message_id, member_id, data):
    avail.cast("Unfortunately, help isn't available for now")


  def __start_game(self, lobby):
    next_ids = []
    for start_message_id in lobby.start_message_ids:
      next_ids_add = lobby.getAcks(start_message_id)
      for p_id in next_ids_add:
        if not p_id in next_ids:
          next_ids.append(p_id)

    if len(next_ids) < 3 or len(next_ids) < lobby.minplayers:
      lobby.cast("Not enough players to start a game")
      return # TODO: Exception
    if len(self.availableComms) < 2:
      lobby.cast("Not enough unused chats to start")
      return # TODO: Exception
    lobby.cast("Starting Game")
    mainComm = self.availableComms.pop()
    mafiaComm = self.availableComms.pop()

    game_id = self.__game_id()
    roles = self.__rolegen(next_ids)
    rules = lobby.rules.copy()

    lobby.mstate = MState(
      game_id, mainComm, mafiaComm, lobby,
      rules, roles, self.RecordType()
    )
    lobby.mstate.start_game()

    lobby.start_timer = None
    lobby.start_message_ids = []

  def __save_rules(self):
    f = open(RULES_FILE_PATH, 'w')
    for rule in self.rules:
        f.write(rule+"|"+self.rules[rule]+"\n")
    f.close()
    return True

  def __load_rules(self):
    rules = {}
    f = open(RULES_FILE_PATH, 'r')
    line = f.readline()
    while '\n' in line:
        words = line.strip().split("|")
        rules[words[0]] = words[1]
        line = f.readline()
    f.close()
    return rules

  def __game_id(self):
    return 1

  def __rolegen(self, p_ids):
    if len(self.determined_roles) > 0:
      roles = {}
      for p_id in p_ids:
        roles[p_id] = self.determined_roles.pop(0)
      return roles
    return {} # TODO: implement
  