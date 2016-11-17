#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import _thread
import time
import json

from MInfo import *
import GroupyComm
import MState

comm = GroupyComm.GroupyComm()
mstate = MState.MState(comm)

DMlock = _thread.allocate_lock()

### POST FUNCTIONS #############################################################

### LOBBY ----------------------------------------------------------------------
def lobby_help(post={},words=[]):
  comm.cast("LOBBY HELP",LOBBY_GROUP_ID)
  return True

def lobby_status(post={},words=[]):
  comm.cast("LOBBY STATUS",LOBBY_GROUP_ID)
  return True

def lobby_start(post={},words=[]):
  # NOTE: When the day is 0, the following is true:
  if mstate.day == 0:
    return mstate.startGame() 
  return False

def lobby_in(post,words=[]):
  log("IN")
  # Get inquirer
  try:
    player = post['user_id']
  except Exception as e:
    log("In failed: couldn't get player: {}".format(e))
    return False
  # Add to list
  if player not in mstate.nextPlayerIDs:
    mstate.nextPlayerIDs.append(player)
    msg = "{} added to next game:\n".format(comm.getName(player))
    for player in mstate.nextPlayerIDs:
      msg = msg + comm.getName(player) + "\n"
    comm.cast(msg,LOBBY_GROUP_ID)
  return True

def lobby_out(post,words=[]):
  log("OUT")
  # Get player
  try:
    player = post['user_id']
  except Exception as e:
    log("Out failed: couldn't get player: {}".format(e))
    return False
  # try to remove from list:
  if player in mstate.nextPlayerIDs: mstate.nextPlayerIDs.remove(player)
  comm.cast("{} removed from next game".format(comm.getName(player)),LOBBY_GROUP_ID)
  return True

def lobby_watch(post,words=[]):
  log("WATCH")
  # Get player
  try:
    player_id = post['user_id']
  except Exception as e:
    log("Watch failed: couldn't get player: {}".format(e))
    return False
  # if they aren't already in the game, add to game
  try:
    if not comm.addMain(player_id):
      log("Failed to add {} as watcher: already in".format(player_id))
      return False
  except Exception as e:
    log("Failed to add {} as watcher: {}".format(player_id,e))
    return False
  return True

    
### MAIN -----------------------------------------------------------------------
    
def vote(post,words):
  log("VOTE")
  # get voter_id
  try:
    voter = post['user_id']
  except Exception as e:
    log("Vote failed: couldn't get voter: {}".format(e))
    return False
  # get votee_id
  try:
    mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
    if not len(mentions) <= 1:
      log("Vote Failed: invalid votee count: {}".format(len(mentions)))
      return False
    elif words[1].lower() == "me":
      votee = voter
    elif words[1].lower() == "none":
      votee = None
    elif words[1].lower() == "nokill":
      votee= "0"
    else:
      votee = mentions[0]['user_ids'][0]
  except Exception as e:
    self.log("Vote Failed: Couldn't get votee: {}".format(e))
    return False
  return mstate.vote(voter,votee)
  

def status(post={},words=[]):
  log("STATUS")
  comm.cast(mstate.__str__())
  return True

def help_(post={},words=[]):
  comm.cast(HELP_MESSAGE)
  return True

def timer(post={},words=[]):
  log("Setting Timer")
  return mstate.setTimer()


### MAFIA POST FUNCTIONS #####################################################

def mafia_help(post={},words=[]):
  comm.cast(M_HELP_MESSAGE,MAFIA_GROUP_ID)
  return True

def mafia_target(post,words):
  try:
    return mstate.mafiaTarget(int(words[1]))
  except Exception as e:
    log("Invalid Mafia Target {}".format(e))
    return False
  
def mafia_options(post={},words=[]):
  return mstate.mafia_options()

### DOCTOR FUNCTIONS #########################################################

def doctor_help(DM,words={}):
  comm.sendDM(DOC_HELP_MESSAGE, DM['sender_id'])
  return True

def doctor_save(DM,words):
  try:
    return mstate.target(DM['sender_id'],int(words[1]))
  except Exception as e:
    log("Doctor save failed: {}".format(e))
  return False

def doctor_options(DM,words={}):
  return mstate.send_options("Use /target number (i.e. /target 0) to pick someone to save",
                             DM['sender_id'])

### COP FUNCTIONS ############################################################

def cop_help(DM,words=[]):
  comm.sendDM(COP_HELP_MESSAGE, DM["sender_id"])
  return True

def cop_investigate(DM,words):
  try:
    return mstate.target(DM['sender_id'],int(words[1]))
  except Exception as e:
    log("Cop investigation failed: {}".format(e))
  return False

def cop_options(DM,words=[]):
  return mstate.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",
                             DM['sender_id'])

### CELEB FN ################################################################

def celeb_help(DM,words=[]):
  comm.sendDM(CELEB_HELP_MESSAGE, DM["sender_id"])
  return True

def celeb_reveal(DM,words=[]):
  return mstate.reveal(DM["sender_id"])


### ANY DM FUNCTIONS ########################################################

def dm_help(DM,words):
  return comm.sendDM(DM_HELP_MESSAGE,DM['sender_id'])

def dm_status(DM,words=[]):
  return comm.sendDM(mstate.__str__(),DM['sender_id'])
  
  
# These dicts routes the command to the correct function

# Lobby operations
LOPS={ HELP_KW   : lobby_help  ,
       STATUS_KW : lobby_status,
       WATCH_KW  : lobby_watch ,
       IN_KW     : lobby_in    ,
       OUT_KW    : lobby_out   ,
       START_KW  : lobby_start ,
     }

OPS ={ VOTE_KW   : vote   ,
       STATUS_KW : status ,
       HELP_KW   : help_  ,
       TIMER_KW  : timer  ,
     }

MOPS={ HELP_KW   : mafia_help ,
       TARGET_KW : mafia_target ,
       OPTS_KW   : mafia_options,
     }

DOC_OPS = {HELP_KW   : doctor_help ,
           OPTS_KW   : doctor_options ,
           TARGET_KW : doctor_save ,
          }
COP_OPS = {HELP_KW   : cop_help ,
           OPTS_KW   : cop_options ,
           TARGET_KW : cop_investigate ,
          }
CELEB_OPS = {HELP_KW : celeb_help,
             REVEAL_KW : celeb_reveal,
             }
DM_OPS = { HELP_KW  : dm_help,
           STATUS_KW: dm_status,
          }
def do_POST_LOBBY(post):
  log("POST in LOBBY")
  try:
    if(post['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = post['text'][len(ACCESS_KW):].split() 
      if(not len(words) == 0 and words[0] in LOPS):
        if not LOPS[words[0]](post,words):
          comm.cast("{} failed".format(words[0]))
      else:
        comm.cast("Invalid request, (try {}{} for help)".format(ACCESS_KW,HELP_KW))
  except KeyError as e: pass

def do_POST_MAIN(post):
  log("POST in MAIN")
  try:
    if(post['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = post['text'][len(ACCESS_KW):].split() 
      if(not len(words) == 0 and words[0] in OPS):
        if not OPS[words[0]](post,words):
          comm.cast("{} failed".format(words[0]))
      else:
        comm.cast("Invalid request, (try {}{} for help)".format(ACCESS_KW,HELP_KW))
  except KeyError as e: pass

def do_POST_MAFIA(post):
  log("Got POST in MAFIA")
  # Test if we need to do anything
  try:
    if(post['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = post['text'][len(ACCESS_KW):].split() 
      if(not len(words) == 0 and words[0] in MOPS):
        if not MOPS[words[0]](post,words):
          comm.cast("{} failed".format(words[0]),MAFIA_GROUP_ID)
      else:
        comm.cast("Invalid request, (try {}{} for help)".format(ACCESS_KW,HELP_KW))
  except KeyError as e: pass

def do_POST(post):
  if(  post['group_id'] == MAIN_GROUP_ID): do_POST_MAIN(post)
  elif(post['group_id'] == MAFIA_GROUP_ID): do_POST_MAFIA(post)
  elif(post['group_id'] == LOBBY_GROUP_ID): do_POST_LOBBY(post)
  mstate.saveNotes()

def do_DM(DM):
  log("Got DM")
  try:
    if(not DM['sender_id'] == MODERATOR and
       DM['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = DM['text'][len(ACCESS_KW):].split()
      try:
        role = mstate.getPlayer(DM['sender_id']).role
      except Exception as e:
        role = ""
     
      if(role == "DOCTOR"):
        if(not len(words) == 0 and words[0] in DOC_OPS):
          if not DOC_OPS[words[0]](DM,words):
            comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
              
      elif(role == "COP"):
        if(not len(words) == 0 and words[0] in COP_OPS):
          if not COP_OPS[words[0]](DM,words):
            comm.sendDM("{} failed".format(words[0]),DM['sender_id'])

      elif(role == "CELEB"):
        if(not len(words) == 0 and words[0] in CELEB_OPS):
          if not CELEB_OPS[words[0]](DM,words):
            comm.sendDM("{} failed".format(words[0]),DM['sender_id'])

      if(not len(words) == 0 and words[0] in DM_OPS):
        if not DM_OPS[words[0]](DM,words):
          comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
      
         
  except Exception as e:
    comm.log("Error doing DM: {}".format(e))

def loopDM():
  while True:
    try:
      for member in comm.getMembers():
        DMs = comm.getDMs(member.user_id)
        for DM in DMs:
          DMlock.acquire()
          do_DM(DM)
          DMlock.release()
        time.sleep(.5)
    except Exception as e:
      log("Error in DMs: {}".format(e))


def loopDMin():
# Specifically, only loop through the players in the game
  while True:
    try:
      for player in mstate.players:
        DMs = comm.getDMs(player.id_)
        for DM in DMs:
          DMlock.acquire()
          do_DM(DM)
          DMlock.release()
        time.sleep(.5)
    except Exception as e:
      log("Error in DMsin: {}".format(e))

class MainHandler(BaseHandler):

  def do_POST(self):
    try:
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except Exception as e:
      post = {}

    try:
      do_POST(post)
    except Exception as e:
      log(e)
    return

if __name__ == "__main__":

  server = HTTPServer((ADDRESS,int(PORT)), MainHandler)

  mstate.loadNotes()

  comm.intro()

  try:
    _thread.start_new_thread(loopDM,())
    _thread.start_new_thread(loopDMin,())
    _thread.start_new_thread(server.serve_forever,())

    while True:
      pass
  except KeyboardInterrupt as e:
    pass

  comm.outro()
 
