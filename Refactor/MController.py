from MInfo import *
from MTimer import MTimer
from MState import MState, GameOverException
from MComm import MComm
from DBMRecord import DBMRecord

import time


# Has a function for every possible command
# Each command fn has a standard form
# These commands form an interface that controls the overall operation of the app

# command(group_id, message_id, member_id, data)

# group_id is the id of the group that the message was sent to.
# member_id is the id of the player who sent the message
# message_id is the id of the message sent
# data will contain any other necessary information for the command to process.

# The server program will process requests and port them into the correct command fn

class MController:

  def __init__(self, lobby_id, group_ids, CommType=MComm):

    # For now, single lobby, single game

    self.mstate = None 
    self.rules = self.__load_rules()

    self.lobbyComm = CommType(lobby_id)
    self.start_timer = None
    self.start_message_ids = []

    self.availableComms = []
    for group_id in group_ids:
      self.availableComms.append(CommType(group_id))
    
    
  def __init_commands(self):
    self.global_commands = {
      START_KW : self.start_command,
      IN_KW    : self.in_command,
      OUT_KW   : self.out_command,
      WATCH_KW : self.watch_command,
      RULE_KW  : self.rule_command,
      STATS_KW : self.stats_command,
      STATUS_KW: self.status_command,
      HELP_KW  : self.help_command,
      LEAVE_KW : self.leave_command,
    }
    self.mstate_commands ={
      VOTE_KW  : self.vote_command,
      TIMER_KW : self.timer_command,
      UNTIMER_KW: self.untimer_command,
      TARGET_KW: self.target_command,

    }

  def command(self, keyword, group_id, message_id, member_id, data):
    """ If this is a DM, group id has a '+' in it, member_id is sender"""
    try:
      mname = keyword + "_command"
      if not hasattr(self, mname):
        return
      method = getattr(self, mname)
      method(group_id, message_id, member_id, data)
    except GameOverException as goe:
      if self.mstate == None:
        pass # Exception
      mstate = self.mstate
      self.availableComms.append(mstate.mafiaComm)
      self.availableComms.append(mstate.mainComm)
      self.mstate = None
    

  def start_command(self, group_id, message_id, member_id, data):
    if not self.start_timer == None:
      self.start_timer.halt()
    self.start_message_ids = []
    # Every lobby has its own controller? No, but for now ok

    # TODO: Add those in current start to interrupting start
    minutes = 1
    minplayers = 3
    words = data['text'].split()
    try:
      if len(words) >= 3:
        minplayers = int(words[2])
      if len(words) >= 2:
        minutes = int(words[1])
    except ValueError:
      pass

    self.minplayers = minplayers
    msg = ("Game will start in {} minute{} ({}). "
           "If there are at least {} players)" 
           " Like this to join.").format(
             minutes, '' if minutes == 1 else 's',
             time.strftime("%I:%M",time.localtime(time.time() + (minutes*60))),
             minplayers
           )

    self.start_message_ids.append(self.lobbyComm.cast(msg))
    alarms = {
      0 : self.__start_game,
    }
    self.start_timer = MTimer(minutes*60, alarms)

  def extend_command(self, group_id, message_id, member_id, data):
    if self.start_timer == None:
      self.lobbyComm.cast("No game is starting")
      return
    words = data['text'].split()
    try:
      minutes = int(words[1])
    except ValueError as e:
      return
    self.start_timer.addTime(minutes*60)
    if self.start_timer.getTime > 10: # If it isn't immediately starting...
      minutes = self.start_timer.getTime() // 60
      msg = ("Game will start in {} minute{} ({}). "
             "You can also like this message now.").format(
               minutes, '' if minutes == 1 else 's',
               time.strftime("%I%M" , time.localtime(time.time()+(minutes*60))),
             )
      self.start_message_ids.append(self.lobbyComm.cast(msg))


  def in_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.cast("Unfortunately, /in doesn't work right now")

  def out_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.cast("Unfortunately, /out doesn't work right now")
    
  def watch_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.ack(message_id)

    if self.mstate == None:
      self.lobbyComm.cast("No game to watch")
      return
    self.mstate.mainComm.add(member_id, self.lobbyComm.getName(member_id))
    
  def rule_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.cast("Unfortunately, rules cannot be changed for now")
    
  def stats_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.ack(message_id)
    msg = CALLBACK_URL + ":" + STATS_PORT
    self.lobbyComm.cast(msg)
    
  def status_command(self, group_id, message_id, member_id, data):

    if group_id == self.lobbyComm.id:
      msg = ""
      if self.mstate == None:
        msg = "No games"
      else:
        msg = str(self.mstate)
      if not self.start_timer == None:
        m = self.start_timer.getTime()
        msg += "\nNew game starting within {} min".format(m//60)
    elif group_id == self.mstate.mainComm.id:
      self.mstate.mainComm.cast(str(self.mstate))
    
  def leave_command(self, group_id, message_id, member_id, data):
    if group_id == self.lobbyComm.id:
      self.lobbyComm.remove(member_id)
    elif group_id == self.mstate.mainComm.id:
      if member_id in [p.id for p in self.mstate.players]:
        self.mstate.mainComm.cast("You can't leave, aren't you playing?")
      else:
        self.mstate.mainComm.remove(member_id)
    
  def help_command(self, group_id, message_id, member_id, data):
    self.lobbyComm.cast("Unfortunately, rules cannot be changed for now")

  def vote_command(self, group_id, message_id, member_id, data):
    if not self.mstate == None and self.mstate.mainComm.id == group_id:
      return #TODO: Exception?

    voter_id = member_id
    # Get mentioned votee
    words = data['text'].split()
    if len(words) < 2:
      votee_id = None
    elif words[1].lower() == "me":
      votee_id = voter_id
    elif words[1].lower() == "nokill":
      votee_id = "0"
    elif 'attachments' in data:
      mentions = [a for a in data['attachments'] if a['type'] == 'mentions']
      if (len(mentions) > 0 and 
          'user_ids' in mentions[0] and 
          len(mentions[0]['user_ids']) >= 1):
        votee_id = mentions[0]['user_ids'][0]
      else:
        votee_id = None
    else:
      votee_id = None
    self.mstate.mainComm.ack(message_id)
    self.mstate.vote(voter_id, votee_id)

  def timer_command(self, group_id, message_id, member_id, data):
    if not self.mstate == None and self.mstate.mainComm.id == group_id:
      return #TODO: Exception?
    self.mstate.setTimer(member_id)
    
  def untimer_command(self, group_id, message_id, member_id, data):
    if not self.mstate == None and self.mstate.mainComm.id == group_id:
      return #TODO: Exception?
    self.mstate.unSetTimer(member_id)
    
  def target_command(self, group_id, message_id, member_id, data):
    if '+' in group_id and not data['sender_id'] == MODERATOR:
      words = data['text'].strip()
      if len(words) < 2:
        return # TODO: Exception
      target_option = words[1]
      if not member_id in [p.id for p in self.mstate.players]:
        return # TODO: Exception
      self.mstate.target(member_id, target_option)

  def options_command(self, group_id, message_id, member_id, data):
    if '+' in group_id and not data['sender_id'] == MODERATOR:
      if not member_id in [p.id for p in self.mstate.players]:
        return # TODO: Exception
      self.mstate.send_options(member_id)

  def reveal_command(self, group_id, message_id, member_id, data):
    if '+' in group_id and not data['sender_id'] == MODERATOR:
      if not member_id in [p.id for p in self.mstate.players]:
        return # TODO: Exception
      self.mstate.try_reveal(member_id)

  def __start_game(self):
    next_ids = []
    for start_message_id in self.start_message_ids:
      next_ids_add = self.lobbyComm.getAcks(start_message_id)
      for p_id in next_ids_add:
        if not p_id in next_ids:
          next_ids.append(p_id)

    if len(next_ids) < 3 or len(next_ids) < self.minplayers:
      self.lobbyComm.cast("Not enough players to start a game")
      return # TODO: Exception
    if len(self.availableComms) < 2:
      self.lobbyComm.cast("Not enough unused chats to start")
      return # TODO: Exception
    self.lobbyComm.cast("Starting Game")
    mainComm = self.availableComms.pop()
    mafiaComm = self.availableComms.pop()

    roles = self.__rolegen(next_ids)

    self.mstate = MState(
      next_ids, mainComm, mafiaComm, self.lobbyComm,
      self.rules, roles, DBMRecord()
    )
    self.mstate.start_game()

    self.start_timer = None
    self.minplayers = 3
    self.start_message_ids = []


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

  def __rolegen(self, p_ids):
    return [] # TODO: implement
  