# Groupy interface module
from MInfo import * # loads in globals
"""
This module handles all the communication with Groupme

you can cast to different groups

you can DM to different players

"""

try:
  import groupy
  import groupy.api.endpoint as groupyEP
except Exception as e:
  log("FAILED TO LOAD GROUPY")

class NoGroupError(Exception):
  def __init__(self,msg):
    self.msg = msg

class NoBotError(Exception):
  def __init__(self,msg):
    self.msg = msg

class GroupyComm:

  def __init__(self):
    # Setup Groups
    try:
      self.lobbyGroup = self.getGroup(LOBBY_GROUP_ID)
      self.lobbyBot   = self.getBot(LOBBY_BOT_ID)

      self.mainGroup  = self.getGroup(MAIN_GROUP_ID)
      self.mainBot    = self.getBot(MAIN_BOT_ID)
      
      self.mafiaGroup = self.getGroup(MAFIA_GROUP_ID)
      self.mafiaBot   = self.getBot(MAFIA_BOT_ID)
    except NoGroupError as e:
      log("FATAL: Failed to load group: {}".format(e))
      exit()
    except NoBotError as e:
      log("FATAL: Failed to load bot: {}".format(e))
      exit()
    except Exception as e:
      log("FATAL: Failed loading Groups: {}".format(e))
      exit()

    # Setup Direct Messages
#    try:
#      self.recent_ids = loadNote("recent_ids")
#    except NoteError as e:
    self.recent_ids = {}


  def getGroup(self,group_id):
    try:
      groups = [g for g in groupy.Group.list() if g.group_id == group_id]
    except Exception as e:
      log("Failed to load group from id {}: {}".format(group_id,e))
      raise e
    if len(groups) >= 1:
      return groups[0]
    else:
      log("No group found with id {}".format(group_id))
      raise NoGroupError("No group found with id {}".format(group_id))

  def getBot(self,bot_id):
    try:
      bots = [b for b in groupy.Bot.list() if b.bot_id == bot_id]
    except Exception as e:
      log("Failed to load bot from id {}: {}".format(bot_id,e))
      raise e
    if len(bots) >= 1:
      return bots[0]
    else:
      log("No bot found with id {}".format(bot_id))
      raise NoBotError("No bot found with id {}".format(bot_id))

  def cast(self,message,group_id=MAIN_GROUP_ID):
    try:
      if not SILENT:
        groupyEP.Messages.create(group_id,message)
      log("CAST: {}".format(message))
      return True
    except Exception as e:
      log("FAILED TO CAST {}: {}".format(message,e))
      return False
    
  def sendDM(self,message,mem_id):
    try:
      if not SILENT:
        groupyEP.DirectMessages.create(mem_id,message)
      log("DM-{}: {}".format(self.getName(mem_id),message))
      return True
    except Exception as e:
      log("FAILED TO DM-{} {}: {}".format(self.getName(mem_id),message,e))
      return False

  def getDMs(self, player_id):
    try:
      if player_id in self.recent_ids:
        DMs = groupyEP.DirectMessages.index(
                player_id,
                since_id=self.recent_ids[player_id])['direct_messages']

        self.recent_ids[player_id] = DMs[0]['id']
      else:
        DMs = groupyEP.DirectMessages.index(player_id)['direct_messages']
        if len(DMs) > 0:
          self.recent_ids[player_id] = DMs[0]['id']
          DMs = []
      saveNote(self.recent_ids,"recent_ids")
      return DMs
    except Exception as e:
      log("Failed to get DM from {}: {}".format(self.getName(player_id),e), 3) # This happens a lot, so it's silenced
      return []

  def getName(self,player_id):
    self.lobbyGroup.refresh()
    members = self.lobbyGroup.members()
    for m in members:
      if m.user_id == player_id:
        return m.nickname
    return "__"

  def getMembers(self):
    self.mainGroup.refresh()
    return self.mainGroup.members()

  def addMain(self, player_id):
    if not player_id in [m.user_id for m in self.getMembers()]:
      self.mainGroup.add({'user_id':player_id, 'nickname':self.getName(player_id)})
      return True
    else:
      return False

  def clearMain(self, saveList=[]):
    # Remove all from Main Group except for those with id in savelist
    self.mainGroup.refresh()
    for mem in self.mainGroup.members():
      if not mem.user_id == MODERATOR and not mem.user_id in saveList:
        self.mainGroup.remove(mem)
        log("removing {} from mafia chat".format(mem.nickname))
    return True

  def addMafia(self, player_id):
    self.mafiaGroup.add({'user_id':player_id})

  def clearMafia(self):
    # Remove all from Mafia Group
    self.mafiaGroup.refresh()
    for mem in self.mafiaGroup.members():
      if not mem.user_id == MODERATOR:
        self.mafiaGroup.remove(mem)
        log("removing {} from mafia chat".format(mem.nickname))
    return True

  def remove(self,player_id):
    for mem in self.mainGroup.members():
      if mem.user_id == player_id:
        self.mainGroup.remove(mem)
    for mem in self.mafiaGroup.members():
      if mem.user_id == player_id:
        self.mafiaGroup.remove(mem)
    return True

  def intro(self):
    if not SILENT:
      groupyEP.Groups.update(LOBBY_GROUP_ID,name="Let's Play Mafia!")
      
  def outro(self):
    if not SILENT: 
      groupyEP.Groups.update(LOBBY_GROUP_ID,name="Let's Play Mafia! [PAUSED]")

class GroupyCommTest:

  def __init__(self):
    log("GroupyComm Init",3)

    self.main = []
    self.mafia = []

  def cast(self,msg,group_id=MAIN_GROUP_ID):
    log("GroupyComm cast",5)
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
    log("GroupyComm sendDM",5)
    log("DM: "+"("+player_id+") "+msg)
    return True

  def getDMs(self,player_id):
    log("GroupyComm getDMs",3)
    return []

  def getName(self,player_id):
    log("GroupyComm getName",5)
    return "[Name of {}]".format(player_id)

  def getMembers(self):
    log("GroupyComm getMembers",3)
    print("Getting Members")
    return []

  def addMafia(self, player_id):
    log("GroupyComm addMafia",3)
    self.mafia.append(player_id)
    return True

  def clearMafia(self):
    log("GroupyComm clearMafia",3)
    self.mafia.clear()
    return True

  def addMain(self, player):
    log("GroupyComm addMain",3)
    if not player in self.main:
      self.main.append(player)
    return True

  def clearMain(self, saveList = []):
    log("GroupyComm clearMain",3)
    for p in self.main:
      if not p in saveList:
        self.main.remove(p)
    return True

  def remove(self, p_id):
    log("GroupyComm remove",3)
    if p_id in self.main:
      self.main.remove(p_id)
    if p_id in self.mafia:
      self.mafia.remove(p_id)
    return True


  def intro(self):
    log("intro")

  def outro(self):
    log("outro")
