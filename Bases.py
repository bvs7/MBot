#!/usr/bin/python3

# Base Classes for each required class. These are implemented as test classes

from MInfo import *

class BaseGroupyComm:

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


class BaseMState:

  def __init__(self,comm):
    log("BaseMState init",3)

  def vote(self,voter_id,votee_id):
    log("BaseMState vote",3)

  def mafiaTarget(self,opt):
    log("BaseMState mafiaTarget",3)

  def mafia_options(self):
    log("BaseMState mafia_options",3)

  def target(self,p,opt):
    log("BaseMState target",3)

  def send_options(self,prompt,p):
    log("BaseMState send_options",3)

  def reveal(self,p):
    log("BaseMState reveal",3)

  def startGame(self):
    log("BaseMState startGame",3)

  def setTimer(self):
    log("BaseMState setTimer",3)

class BaseMServer:

  def __init__(self, CommType=BaseGroupyComm, MStateType=BaseMState):
    log("BaseMServer init",3)
    self.comm = CommType()
    self.mstate = MStateType(self.comm)

    self._init_OPS()            

  def do_POST(self,post):
    log("BaseMServer do_POST",3)
    if post['text'][0:len(ACCESS_KW)] == ACCESS_KW:
      words = post['text'][len(ACCESS_KW):].split()
      ops = {}
      if(  post['group_id'] == MAIN_GROUP_ID):  ops = self.OPS
      elif(post['group_id'] == MAFIA_GROUP_ID): ops = self.MOPS
      elif(post['group_id'] == LOBBY_GROUP_ID): ops = self.LOPS
      else:
        log("POST group_id not found: {}".format(post['group_id']))
        return False
      return self._do_POST_OPS(post,words,ops)

  def do_DM(self,DM):
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
      ops = self.DM_OPS
      if(not len(words) == 0):
        if(role == "DOCTOR" and words[0] in self.DOC_OPS):
          ops = self.DOC_OPS
        elif(role == "COP" and words[0] in self.COP_OPS):
          ops = self.COP_OPS
        elif(role == "CELEB" and words[0] in self.CELEB_OPS):
          ops = self.CELEB_OPS
      if not ops[words[0]](DM,words):
        self.comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
        return False
    return True

  #### HELPER FN ####

  def _do_POST_OPS(self,post,words,ops):
    log("BaseMServer _do_POST_OPS",4)
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
    return True

  def _init_OPS(self):

    # Lobby Options
    self.LOPS={ HELP_KW   : self._lobby_help   ,
                STATUS_KW : self._lobby_status ,
                START_KW  : self._lobby_start  ,
                IN_KW     : self._lobby_in     ,
                OUT_KW    : self._lobby_out    ,
                WATCH_KW  : self._lobby_watch  ,
              }

    # Main OPS
    self.OPS ={ VOTE_KW   : self._vote   ,
                STATUS_KW : self._status ,
                HELP_KW   : self._help   ,
                TIMER_KW  : self._timer  ,
              }

    # Mafia OPS
    self.MOPS={ HELP_KW   : self._mafia_help    ,
                TARGET_KW : self._mafia_target  ,
                OPTS_KW   : self._mafia_options ,
              }

    self.DOC_OPS = { HELP_KW    : self._doc_help ,
                     OPTS_KW    : self._doc_options ,
                     TARGET_KW  : self._doc_save ,
                   }
    self.COP_OPS = { HELP_KW    : self._cop_help ,
                     OPTS_KW    : self._cop_options ,
                     TARGET_KW  : self._cop_investigate ,
                   }
    self.CELEB_OPS={ HELP_KW    : self._celeb_help,
                     REVEAL_KW  : self._celeb_reveal,
                   }
    self.DM_OPS =  { HELP_KW    : self._dm_help,
                     STATUS_KW  : self._dm_status,
                   }

  ### LOBBY GROUP FN -----------------------------------------------------------
    
  def _lobby_help(self,post={},words=[]):
    log("BaseMServer _lobby_help",5)
    self.comm.cast(L_HELP_MESSAGE,LOBBY_GROUP_ID)
    return True

  def _lobby_status(self,post={},words=[]):
    log("BaseMServer _lobby_status",5)
    self.comm.cast(mstate.__str__(),LOBBY_GROUP_ID)
    return True

  def _lobby_start(self,post={},words=[]):
    log("BaseMServer _lobby_start",5)
    # NOTE: When the day is 0, the following is true:
    if self.mstate.day == 0:
      return self.mstate.startGame() 
    else:
      self.comm.cast("A game is already in progress. Watch with {}{}".format(ACCESS_KW,WATCH_KW),
                     LOBBY_GROUP_ID)
      return True

  def _lobby_in(self,post,words=[]):
    log("BaseMServer _lobby_in",5)
    assert 'user_id' in post, "No user_id in _lobby_in post"
    # Get player to go in
    player_id = post['user_id']
    # Add to next list
    if player_id not in self.mstate.nextPlayerIDs:
      self.mstate.nextPlayerIDs.append(player_id)
      msg = "{} added to next game:\n".format(self.comm.getName(player))
    else:
      self.comm.cast("You are already in the next game:",LOBBY_GROUP_ID)
    for player in mstate.nextPlayerIDs:
      msg = msg + self.comm.getName(player) + "\n"
    self.comm.cast(msg,LOBBY_GROUP_ID)
    return True

  def _lobby_out(self,post,words=[]):
    log("BaseMServer _lobby_out",5)
    assert 'user_id' in post, "No user_id in _lobby_out post"
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

  def _lobby_watch(self,post,words=[]):
    log("BaseMServer _lobby_watch",5)
    if self.mstate.day == 0:
      self.comm.cast("No game to watch",LOBBY_GROUP_ID)
      return True
    assert 'user_id' in post, "No user_id in _lobby_watch post"
    player_id = post['user_id']
    # if they aren't already in the game, add to game
    return self.comm.addMain(player_id)

  ### MAIN GROUP FN ------------------------------------------------------------

  def _vote(self,post,words):
    log("BaseMServer _vote",5)
    assert 'user_id' in post, "No user_id in _vote post"
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

  def _status(self,post={},words=[]):
    log("BaseMServer _status",5)
    self.comm.cast(mstate.__str__())
    return True

  def _help(self,post={},words=[]):
    log("BaseMServer _help",5)
    self.comm.cast(HELP_MESSAGE)
    return True

  def _timer(self,post={},words=[]):
    log("BaseMServer _timer",5)
    return self.mstate.setTimer()

  ### MAFIA GROUP FN -----------------------------------------------------------

  def _mafia_help(self,post={},words=[]):
    log("BaseMServer _mafia_help",5)
    self.comm.cast(M_HELP_MESSAGE,MAFIA_GROUP_ID)
    return True

  def _mafia_target(self,post,words):
    log("BaseMServer _mafia_target",5)
    try:
      return self.mstate.mafiaTarget(int(words[1]))
    except Exception as e:
      log("Invalid Mafia Target {}".format(e))
      return False
    

  def _mafia_options(self,post={},words=[]):
    log("BaseMServer _mafia_options",5)
    return self.mstate.mafia_options()

  ### DOC DM FN ----------------------------------------------------------------

  def _doc_help(self,DM,words=[]):
    log("BaseMServer _doc_help",5)
    self.comm.sendDM(DOC_HELP_MESSAGE, DM['sender_id'])
    return True

  def _doc_save(self,DM,words):
    log("BaseMServer _doc_save",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Doctor save failed: {}".format(e))
    return False

  def _doc_options(self,DM,words=[]):
    log("BaseMServer _doc_options",5)
    return self.mstate.send_options("Use /target number (i.e. /target 0) to pick someone to save",
                                    DM['sender_id'])

  ### COP DM FN ----------------------------------------------------------------

  def _cop_help(self,DM,words=[]):
    log("BaseMServer _cop_help",5)
    self.comm.sendDM(COP_HELP_MESSAGE, DM["sender_id"])
    return True

  def _cop_investigate(self,DM,words):
    log("BaseMServer _cop_investigate",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Cop investigation failed: {}".format(e))
    return False

  def _cop_options(Self,DM,words=[]):
    log("BaseMServer _cop_options",5)
    return self.mstate.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",
                                    DM['sender_id'])

  ### CELEB DM FN --------------------------------------------------------------

  def _celeb_help(self,DM,words=[]):
    log("BaseMServer _celeb_help",5)
    self.comm.sendDM(CELEB_HELP_MESSAGE, DM["sender_id"])
    return True

  def _celeb_reveal(self,DM,words=[]):
    log("BaseMServer _celeb_reveal",5)
    return self.mstate.reveal(DM["sender_id"])

  ### DM FN --------------------------------------------------------------------

  def _dm_help(self,DM,words):
    log("BaseMServer _dm_help",5)
    return self.comm.sendDM(DM_HELP_MESSAGE,DM['sender_id'])

  def _dm_status(self,DM,words=[]):
    log("BaseMServer _dm_status",5)
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


