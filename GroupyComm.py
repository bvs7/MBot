# Groupy interface module
"""
This module handles all the communication with Groupme

you can cast to different groups

you can DM to different players

"""

import groupy
import groupy.api.endpoint as groupyEP

from MInfo import * # loads in globals

class NoGroupError(Exception):
  def __init__(self,msg):
    self.msg = msg

class NoBotError(Exception):
  def __init__(self,msg):
    self.msg = msg

class GroupyComm:

  def __init__(self):

    log("init")

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

    log("passed groups")

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


  def getDMs(self, player_id):
    """Return a list of the most recent messages from a player"""
    if player_id in self.recent_ids:
      DMs = groupyEP.DirectMessages.index(player_id,
                                          since_id=self.recent_ids[player_id])
      self.recent_ids[player_id] = DMs[0]['id']
    else:
      DMs = groupyEP.DirectMessages.index(player_id)
      self.recent_ids[player_id] = DMs[0]['id']
      DMs = []
    return DMs
    
