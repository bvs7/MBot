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
  pass

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
    try:
      self.recent_ids = loadNote("recent_ids")
    except NoteError as e:
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
      log("CAST-{}: {}".format(group.name,message))
      return True
    except Exception as e:
      log("FAILED TO CAST-{} {}: {}".format(group.name,message,e))
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
        DMs = groupyEP.DirectMessages.index(player_id,
                                            since_id=self.recent_ids[player_id])
        self.recent_ids[player_id] = DMs[0]['id']
      else:
        DMs = groupyEP.DirectMessages.index(player_id)
        self.recent_ids[player_id] = DMs[0]['id']
        DMs = []
      return DMs
    except groupyEP.APIError as e:
      log("Failed to get DM: {}".format(e), 3) # This happens a lot, so it's silenced

  def getName(self,player_id):
    self.mainGroup.refresh()
    members = self.mainGroup.members()
    for m in members:
      if m.user_id == player_id:
        return m.nickname
    return "__"

  def addMafia(self, player_id):
    self.mafiaGroup.add({'user_id':player_id})

  def clearMafia(self):
    # Remove all from Mafia Group
    self.mafiaGroup.refresh()
    for mem in self.mafiaGroup.members():
      if not mem.user_id == self.MODERATOR:
        self.mafiaGroup.remove(mem)
        log("removing {} from mafia chat".format(mem.nickname))

  def intro(self):
    if not SILENT:
      groupyEP.Groups.update(MAIN_GROUP_ID,name="Let's Play Mafia!")
      
  def outro(self):
    if not SILENT: 
      groupyEP.Groups.update(MAIN_GROUP_ID,name="Let's Play Mafia! [PAUSED]")

class GroupyCommTest:

  def __init__(self):
    self.mainGroup = 1
    self.mafiaGroup = 2

    self.mafia = []

  def cast(self,msg,group=1):
    m = "CAST: "
    if group == self.mainGroup:
      m += "(MAIN) "
    elif group == self.mafiaGroup:
      m += "(MAFIA) "
    m += msg

    log(m,1)

  def sendDM(self,msg,player_id):
    log("DM: "+"("+player_id+") "+msg)

  def getDMs(self,player_id):
    return []

  def getName(self,player_id):
    return "[Name of {}]".format(player_id)

  def addMafia(self, player_id):
    self.mafia.append(player_id)

  def clearMafia(self):
    self.mafia.clear()

  
