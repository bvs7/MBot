#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import _thread
import time
import json

from MInfo import *
import GroupyComm
import MState


class MServer:

  def __init__(self, CommType=GroupyComm.GroupyComm,
                     MStateType=MState.MState,
                     restart=True):
    log("MServer init",3)
    self.comm = CommType()
    self.mstate = MStateType(self.comm, restart)

    self.__init_OPS()

  def do_POST(self,post):
    """Process a POST request from bots watching the chats"""
    log("MServer do_POST",3)
    if post['text'][0:len(ACCESS_KW)] == ACCESS_KW:
      words = post['text'][len(ACCESS_KW):].split()
      ops = {}
      if(  post['group_id'] == MAIN_GROUP_ID):  ops = self.__OPS
      elif(post['group_id'] == MAFIA_GROUP_ID): ops = self.__MOPS
      elif(post['group_id'] == LOBBY_GROUP_ID): ops = self.__LOPS
      else:
        # Check if this was posted by the DM bot
        if '+' in post['group_id']:
          return self.do_DM(post)
        log("POST group_id not found: {}".format(post['group_id']))
        return False
      return self.__do_POST_OPS(post,words,ops)

  def do_DM(self,DM):
    """Process a DM from a player"""
    log("MServer do_DM",3)
    assert 'sender_id' in DM, "No sender_id in DM for do_DM"
    assert 'text' in DM, "No text in DM for do_DM"
    if (not DM['sender_id'] == MODERATOR and
        DM['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = DM['text'][len(ACCESS_KW):].split()
      try:
        role = self.mstate.getPlayer(DM['sender_id']).role
      except Exception as e:
        log(e)
        role = ""
      ops = self.__DM_OPS
      if(not len(words) == 0):
        if(role == "DOCTOR" and words[0] in self.__DOC_OPS):
          ops = self.__DOC_OPS
        elif(role == "COP" and words[0] in self.__COP_OPS):
          ops = self.__COP_OPS
        elif(role == "CELEB" and words[0] in self.__CELEB_OPS):
          ops = self.__CELEB_OPS
      if words[0] in ops:
        if not ops[words[0]](DM,words):
          self.comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
          return False
      else:
        self.comm.sendDM("Invalid command: {}".format(words[0]),DM['sender_id'])
    self.mstate.saveNotes()
    return True

  #### HELPER FN ####

  def __do_POST_OPS(self,post,words,ops):
    """Process a POST split into words, using a dict of operations"""
    log("MServer __do_POST_OPS",4)
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
    log("MServer __lobby_help",5)
    self.comm.cast(L_HELP_MESSAGE,LOBBY_GROUP_ID)
    return True

  def __lobby_status(self,post={},words=[]):
    log("MServer __lobby_status",5)
    self.comm.cast(self.mstate.__str__(),LOBBY_GROUP_ID)
    return True

  def __lobby_start(self,post={},words=[]):
    log("MServer __lobby_start",5)
    # NOTE: When the day is 0, the following is true:
    if self.mstate.day == 0:
      return self.mstate.startGame()
    else:
      self.comm.cast("A game is already in progress. Watch with {}{}".format(ACCESS_KW,WATCH_KW),
                     LOBBY_GROUP_ID)
      return True

  def __lobby_in(self,post,words=[]):
    log("MServer __lobby_in",5)
    assert 'user_id' in post, "No user_id in __lobby_in post"
    # Get player to go in
    player_id = post['user_id']
    # Add to next list
    return self.mstate.inNext(player_id)

  def __lobby_out(self,post,words=[]):
    log("MServer __lobby_out",5)
    assert 'user_id' in post, "No user_id in __lobby_out post"
    player_id = post['user_id']
    # try to remove from list:
    if player_id in self.mstate.nextPlayerIDs:
      self.mstate.nextPlayerIDs.remove(player)
      self.comm.cast("{} removed from next game".format(self.comm.getName(player)),
                     LOBBY_GROUP_ID)
    else:
      self.comm.cast("{} wasn't in the next game".format(self.comm.getName(player)),
                     LOBBY_GROUP_ID)
    return True

  def __lobby_watch(self,post,words=[]):
    log("MServer __lobby_watch",5)
    if self.mstate.day == 0:
      self.comm.cast("No game to watch",LOBBY_GROUP_ID)
      return True
    assert 'user_id' in post, "No user_id in __lobby_watch post"
    player_id = post['user_id']
    # if they aren't already in the game, add to game
    return self.comm.addMain(player_id)

  ### MAIN GROUP FN ------------------------------------------------------------

  def __vote(self,post,words):
    log("MServer __vote",5)
    assert 'user_id' in post, "No user_id in __vote post"
    voter = post['user_id']

    if words[1].lower() == "me":
      votee = voter
    elif words[1].lower() == "none":
      votee = None
    elif words[1].lower() == "nokill":
      votee = "0"
    elif ('attachments' in post):
      mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
      if len(mentions):
        assert 'user_ids' in mentions[0] and len(mentions[0]['user_ids']) >= 1, "No user_ids in mention in _vote post"
        votee = mentions[0]['user_ids'][0]
    else:
      self.log("Vote Failed: couldn't get votee")
      return False
    return self.mstate.vote(voter,votee)

  def __status(self,post={},words=[]):
    log("MServer __status",5)
    self.comm.cast(self.mstate.__str__())
    return True

  def __help(self,post={},words=[]):
    log("MServer __help",5)
    self.comm.cast(HELP_MESSAGE)
    return True

  def __timer(self,post={},words=[]):
    log("MServer __timer",5)
    return self.mstate.setTimer()

  ### MAFIA GROUP FN -----------------------------------------------------------

  def __mafia_help(self,post={},words=[]):
    log("MServer __mafia_help",5)
    self.comm.cast(M_HELP_MESSAGE,MAFIA_GROUP_ID)
    return True

  def __mafia_target(self,post,words):
    log("MServer __mafia_target",5)
    try:
      return self.mstate.mafiaTarget(int(words[1]))
    except Exception as e:
      log("Invalid Mafia Target {}".format(e))
      return False


  def __mafia_options(self,post={},words=[]):
    log("MServer __mafia_options",5)
    return self.mstate.mafiaOptions()

  ### DOC DM FN ----------------------------------------------------------------

  def __doc_help(self,DM,words=[]):
    log("MServer __doc_help",5)
    self.comm.sendDM(DOC_HELP_MESSAGE, DM['sender_id'])
    return True

  def __doc_save(self,DM,words):
    log("MServer __doc_save",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Doctor save failed: {}".format(e))
    return False

  def __doc_options(self,DM,words=[]):
    log("MServer __doc_options",5)
    return self.mstate.sendOptions("Use /target number (i.e. /target 0) to pick someone to save",
                                    DM['sender_id'])

  ### COP DM FN ----------------------------------------------------------------

  def __cop_help(self,DM,words=[]):
    log("MServer __cop_help",5)
    self.comm.sendDM(COP_HELP_MESSAGE, DM["sender_id"])
    return True

  def __cop_investigate(self,DM,words):
    log("MServer __cop_investigate",5)
    try:
      return self.mstate.target(DM['sender_id'],int(words[1]))
    except Exception as e:
      log("Cop investigation failed: {}".format(e))
    return False

  def __cop_options(Self,DM,words=[]):
    log("MServer __cop_options",5)
    return self.mstate.sendOptions("Use /target number (i.e. /target 2) to pick someone to investigate",
                                    DM['sender_id'])

  ### CELEB DM FN --------------------------------------------------------------

  def __celeb_help(self,DM,words=[]):
    log("MServer __celeb_help",5)
    self.comm.sendDM(CELEB_HELP_MESSAGE, DM["sender_id"])
    return True

  def __celeb_reveal(self,DM,words=[]):
    log("MServer __celeb_reveal",5)
    return self.mstate.reveal(DM["sender_id"])

  ### DM FN --------------------------------------------------------------------

  def __dm_help(self,DM,words):
    log("MServer __dm_help",5)
    return self.comm.sendDM(DM_HELP_MESSAGE,DM['sender_id'])

  def __dm_status(self,DM,words=[]):
    log("MServer __dm_status",5)
    return self.comm.sendDM(self.mstate.__str__(),DM['sender_id'])



if __name__ == "__main__":
  mserver = MServer()

  DMlock = _thread.allocate_lock()


def loopDM():
  while True:
    try:
      for member in mserver.comm.getMembers():
        DMs = mserver.comm.getDMs(member.user_id)
        for DM in DMs:
          DMlock.acquire()
          mserver.do_DM(DM)
          DMlock.release()
        time.sleep(.5)
    except Exception as e:
      log("Error in DMs: {}".format(e))


def loopDMin():
# Specifically, only loop through the players in the game
  while True:
    try:
      for player in mserver.mstate.players:
        DMs = mserver.comm.getDMs(player.id_)
        for DM in DMs:
          DMlock.acquire()
          mserver.do_DM(DM)
          DMlock.release()
        time.sleep(.5)
    except Exception as e:
      log("Error in DMsin: {}".format(e))

class MainHandler(BaseHandler):

  def do_POST(self):
    try:
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
#      print(content)
      post = json.loads(content)
    except Exception as e:
      post = {}
      log("failed to load content")

    try:
      mserver.do_POST(post)
    except Exception as e:
      log(e)
    return

if __name__ == "__main__":

  server = HTTPServer((ADDRESS,int(PORT)), MainHandler)

  mserver.comm.intro()

  try:
#    _thread.start_new_thread(loopDM,())
#    _thread.start_new_thread(loopDMin,())
    _thread.start_new_thread(server.serve_forever,())

    while True:
      pass
  except KeyboardInterrupt as e:
    pass

  mserver.comm.outro()
