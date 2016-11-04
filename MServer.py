#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import _thread

from MInfo import *
import GroupyComm
import MState

comm = GroupyComm.GroupyComm()
mstate = MState.MState(comm)

### POST FUNCTIONS #############################################################
    
### VOTE -----------------------------------------------------------------------
    
def vote(post,words):
  """{}{} @[player]  - Vote for someone. Once they have a majority of votes they are killed"""
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
  """{}{}  - Check the status of the game"""
  log("STATUS")
  comm.cast(mstate.__str__())
  return True

def help_(post={},words=[]):
  """{}{}  - Display this message"""
  comm.cast(HELP_MESSAGE)
  return True

def start(post={},words=[]):
  """{}{}  - Start a game with the current players"""
  # NOTE: When the day is 0, the following is true:
  if mstate.day == 0:
    return mstate.startGame() 
  return False

def in_(post,words=[]):
  """{}{}  - Join the next game"""
  log("IN")
  # Get inquirer
  try:
    player = post['user_id']
  except Exception as e:
    log("In failed: couldn't get voter: {}".format(e))
    return False
  # Add to list
  if player not in mstate.nextPlayerIDs:
    mstate.nextPlayerIDs.append(player)
    msg = "{} added to next game:\n".format(comm.getName(player))
    for player in mstate.nextPlayerIDs:
      msg = msg + comm.getName(player) + "\n"
    comm.cast(msg)
  return True

def out(post,words=[]):
  """{}{}  - Leave the next game"""
  log("OUT")
  # Get player
  try:
    player = post['user_id']
  except Exception as e:
    log("Out failed: couldn't get voter: {}".format(e))
    return False
  # try to remove from list:
  if player in mstate.nextPlayerIDs: mstate.nextPlayerIDs.remove(player)
  comm.cast("{} removed from game".format(comm.getName(player)))
  return True


### MAFIA POST FUNCTIONS #####################################################

def mafia_help(post={},words=[]):
  """{}{}  - Display this message"""
  comm.cast(M_HELP_MESSAGE,MAFIA_GROUP_ID)
  return True

def mafia_target(post,words):
  """{}{} [number]  - Kill the player associated with this number (from options)"""
  try:
    return mstate.mafiaTarget(int(words[1]))
  except Exception as e:
    log("Invalid Mafia Target {}".format(e))
    return False
  
def mafia_options(post={},words=[]):
  """{}{}  - List the options to kill and the numbers to use to kill them"""
  return mstate.mafia_options()

### DOCTOR FUNCTIONS #########################################################

def doctor_help(DM,words={}):
  """{}{}  - Display this message"""
  comm.sendDM(DOC_HELP_MESSAGE, DM['sender_id'])
  return True

def doctor_save(DM,words):
  """{}{} #  - Try to save the person associated with this number tonight"""
  try:
    return mstate.target(DM['sender_id'],int(words[1]))
  except Exception as e:
    log("Doctor save failed: {}".format(e))
  return False

def doctor_options(DM,words={}):
  """{}{}  - List the options to target and the numbers to use to save them"""
  return mstate.send_options("Use /target number (i.e. /target 0) to pick someone to save",
                             DM['sender_id'])

### COP FUNCTIONS ############################################################

def cop_help(DM,words=[]):
  """{}{}  - Display this message"""
  comm.sendDM(COP_HELP_MESSAGE, DM["sender_id"])
  return True

def cop_investigate(sDM,words):
  """{}{} #  - Try to save the person associated with this number tonight"""
  try:
    return mstate.target(DM['sender_id'],int(words[1]))
  except Exception as e:
    log("Cop investigation failed: {}".format(e))
  return False

def cop_options(DM,words=[]):
  """{}{}  - List the options to target and the numbers to use to investigate them"""
  return mstate.send_options("Use /target number (i.e. /target 2) to pick someone to investigate",
                             DM['sender_id'])

### ANY DM FUNCTIONS ########################################################

def dm_help(DM,words):
  """{}{}  - Get this help message""".format(ACCESS_KW,HELP_KW)
  return comm.sendDM(DM_HELP_MESSAGE,DM['sender_id'])

def dm_status(DM,words=[]):
  """{}{}  - Get the current state of the game""".format(ACCESS_KW,STATUS_KW)
  return comm.sendDM(mstate.__str__,DM['sender_id'])
  
  
# This dict routes the command to the correct function
OPS ={ VOTE_KW   : vote   ,
       STATUS_KW : status ,
       HELP_KW   : help_  ,
       START_KW  : start  ,
       IN_KW     : in_    ,
       OUT_KW    : out    ,
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
DM_OPS = { HELP_KW  : dm_help,
           STATUS_KW: dm_status,
          }

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
  mstate.saveNotes()

def do_DM(DM):
  log("Got DM")
  try:
    if(not DM['sender_id'] == MODERATOR and
       DM['text'][0:len(ACCESS_KW)] == ACCESS_KW):
      words = DM['text'][len(ACCESS_KW):].split()
      player = mstate.getPlayer(DM['sender_id'])
      
      if(player.role == "DOCTOR"):
        if(not len(words) == 0 and words[0] in DOC_OPS):
          if not DOC_OPS[words[0]](DM,words):
            comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
              
      elif(player.role == "COP"):
        if(not len(words) == 0 and words[0] in COP_OPS):
          if not COP_OPS[words[0]](DM,words):
            comm.sendDM("{} failed".format(words[0]),DM['sender_id'])

      if(not len(words) == 0 and words[0] in DM_OPS):
        if not DM_OPS[words[0]](DM,words):
          comm.sendDM("{} failed".format(words[0]),DM['sender_id'])
      
         
  except Exception as e:
    self.log("Error doing DM: {}".format(e))

def loopDM():
  while True:
    for player in mstate.players:
      DMs = comm.getDMs(player.id_)
      for DM in DMs:
        do_DM(DM)

class MainHandler(BaseHandler):

  def do_POST(self):
    try:
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except Exception as e:
      post = {}

    do_POST(post)
    return

if __name__ == "__main__":

  server = HTTPServer((ADDRESS,int(PORT)), MainHandler)

  mstate.loadNotes()

  comm.intro()

  try:
    _thread.start_new_thread(loopDM,())
    _thread.start_new_thread(server.serve_forever,())

    while True:
      pass
  except KeyboardInterrupt as e:
    pass

  comm.outro()
  
  

