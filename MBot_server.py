#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer
import groupy
import groupy.api.endpoint as groupyEP
import random
import json
import _thread # to run both servers at once
import time

### ADMINISTRATIVE CONSTANTS ###

DEBUG = 1


ADDRESS   = '0.0.0.0'
PORT1     = 1121
PORT2     = 1121
#### THESE (should be) LOADED FROM loadInfo()
GROUP_ID  = '25833774' # Let's Play Mafia
MAFIA_ID  = 0 # Mafia group
MBOT_ID   = 0
EVIL_MBOT_ID = 0
####

CALLBACK_URL_MAIN  = 'http://24.59.62.95:'+str(PORT1)
CALLBACK_URL_MAFIA = 'http://24.59.62.95:'+str(PORT2)

MODERATOR = '43040067'

INTRO     = True
OUTRO     = True
NONAME    = ': '

VARIABLES_TO_SAVE = ['GROUP_ID','MAFIA_ID','MBOT_ID','EVIL_MBOT_ID']

### ADMINISTRATIVE VARIABLES ###

group         = 0
mafia_group   = 0
members       = 0
mafia_members = 0
mbot          = 0
evil_mbot     = 0


######## GAME VARIABLES ########

# OP KEYWORDS
ACCESS_KW = '\\'
VOTE_KW   = 'vote'
STATUS_KW = 'status'
HELP_KW   = 'help'
START_KW  = 'start'

# ROLES
TOWN_ROLES = ["TOWN", "COP", "DOCTOR"]
MAFIA_ROLES = ["MAFIA"]

# GAME STATE VARIABLES
GameOn = False
votes  = {}
players= {}
Time   = {'Day':0,'Time':"Day"} # Format Day Number, Day/Night
num_mafia = 0

# [Num People] : [num mafia]
GAME_COUNTS  = {
                 3 : 1,  4 : 1,  5 : 1,  6 : 1,  7 : 1,  8 : 2,  9 : 2,  10 : 3,
                11 : 3,  12 : 3, 13 : 3, 14 : 4, 15 : 4, 16 : 4, 17 : 5, 18 : 5,
                19 : 5,  20 : 5, 21 : 6, 22 : 6, 23 : 6, 24 : 6, 25 : 6, 26 : 6,
                27 : 6,
          }
             

HELP_MESSAGE = """MBot helps this groupme play Mafia
VOTING:
{ACCESS_KW}{VOTE_KW} @[player]
    Cast your vote for a player. Once there is a majority, they die
STATUS:
{ACCESS_KW}{STATUS_KW}
    Shows who is currently in the game and where votes stand
HELP: 
{ACCESS_KW}{HELP_KW}
    Display this message
START:
{ACCESS_KW}{START_KW}
    Start a new game (Only works when no game is afoot)
""".format(**locals())

### FILENAMES ###

NOTES     = './notes'
INFO      = './info'

### Define operations ###

def vote(post):
  log("Vote")

  # Ensure Time is Day
  if not Time['Time'] == 'Day' or not GameOn:
    log("Vote Failed: Not Day")
    return False
  
  # Get voter
  try:
    voter = str(post['user_id'])
  except Exception as e:
    log("Vote Failed: couldn't find voter: {}".format(e))
    return False
  # Get votee
  try:
    mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
    if not len(mentions) == 1:
      log("Vote Failed: invalid votee count: {}".format(len(mentions)))
      return False
  except Exception as e:
    log("Vote Failed: Couldn't get votee: {}".format(e))
    return False

  # Ensure vote is not for moderator

  if votee == MODERATOR:
    log("Vote failed: Tried to vote for Moderator")
    cast("HOW DARE YOU",group)
    return False

  
  # Change vote
  votes[voter] = votee
  log("Vote succeeded: {} changed vote to {}".format(voter,votee))
  testKillVotes(votee)
  return True

def status(post):
  log("Status")
  # Output players and who is voting for who
  reply = "[Alive]:[Votes]\n"
  for m in members:
    reply = reply + getName(m) + " :"
    for voter in votes:
      if(votes[voter] == m):
        reply = reply + getName(voter)
    reply = reply + "\n"
  cast(reply,group)
  return True

def help_(post):
  log("Help")
  cast(HELP_MESSAGE,group)
  return True

def start(post):
  log("Start")
  if not GameOn:
    return genGame()
  return False

# This dict routes the command to the correct function
OPS = { VOTE_KW   : vote   ,
        STATUS_KW : status ,
        HELP_KW   : help_  ,
        START_KW  : start  ,
      }


### HANDLER ###

class MainHandler(BaseHandler):
  
  def do_POST(self):
    log("Got POST")
    try:
      # Get contents of the POST
      length = int(self.headers['Content-length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except KeyError as e:
      post = {}
    except ValueError as e:
      post = {}
    
    words = []

    if(  post['group_id'] == GROUP_ID): self.do_POST_MAIN(post)
    elif(post['group_id'] == MAFIA_ID): self.do_POST_MAFIA(post)


  def do_POST_MAIN(self,post):
    log("Got POST in MAIN")
    # Test if we need to do anything
    try:
      if(post['text'][0:len(ACCESS_KW)] == ACCESS_KW):
        log("Is Access")
        words = post['text'][len(ACCESS_KW):].split()

        if(not len(words) == 0 and words[0] in OPS):
          log("Type: {}".format(words[0]))
          if not OPS[words[0]](post):
            cast("{} failed".format(words[0]),group)
        else:
          cast("Invalid request, (try {ACCESS_KW}{HELP_KW} for help)".format(**locals),group)
    except KeyError as e:
      return

  def do_POST_MAFIA(self,post):
    log("Got POST in MAFIA")


### HELPER FUNCTIONS ###

def testKillVotes(votee):
  # Get people voting for votee
  voters = [v for v in votes if votes[v] == votee]
  
  # If the number of votes is in the majority, kill
  if len(voters) > int(len(members)/2):
    cast("The vote to kill {} has passed".format(getName(votee)),group)
    note("Kill: {}".format(votee))
    if (kill(votee)):
      return True
  return False

def kill(votee):
  # Remove from players
  try:
    group.remove(getMem(votee))
    role = players.pop(votee)
    if role in MAFIA_ROLES:
      num_mafia = num_mafia - 1
  except Exception as e:
    log("Failed to kill {}: {}".format(votee,e))
    return False
  # Check win conditions
  if num_mafia == 0:
    GameOn = False
    cast("TOWN WINS",group)
    return True
  if num_mafia >= (len(players))/2:
    GameOn = False
    cast("MAFIA WINS",group)
    return True
  return True

def genGame():
  log("Generating Game...")
  players = {}

  # Clear aux groups
  log("Removing all from mafia group")
  for mem in mafia_group.members():
    if not mem.user_id == MODERATOR:
      mafia_group.remove(mem)
  log("Figure out game size")
  # Refresh Members in the group
  members = group.members()
  # Find how many mafia there should be
  num_mafia = GAME_COUNTS[len(members)-1] # -1 for not Moderator
  # Randomly order members
  roles = list(range(len(members)))
  random.shuffle(roles)

  # Assign roles
  log("Assigning roles")
  for i in range(len(members)):
    if roles[i] < num_mafia: # First few are mafia
      players[mem.user_id] = "MAFIA"
    elif roles[i] == num_mafia: # Then cop
      players[mem.user_id] = "COP"
    elif roles[i] == num_mafia+1: # Then Doc
      players[mem.user_id] = "DOCTOR"
    else:
      player[mem.user_id] = "TOWN"
 
  log("Adding mafia to groups")
  # add to special groups
  for player in players:
    if players[player] == MAFIA_TEAM:
      mafia_group.add(getMem(player))
      
  GameOn=True
  Time = {'Day' : 1, 'Time' : 'Day'}

  cast("The game has started! There are {} people total and {} mafia.\
        It is the dawn of the first day! Kill someone!",group)
  return True

def regenGame(notes):
  return  

def cast(message, group):
  try:
    groupyEP.Messages.create(group.group_id,message)
    log("CAST-{}: {}".format(group.name,message))
    return True
  except Exception as e:
    log("FAILED to CAST-{} {}: {}".format(group.name,message,e))
    return False
  
def loadNotes():
  note = []
  try:
    f = open(NOTES,'r')
    note = f.readlines()
    f.close()
  except Exception as e:
    log("Error loading notes: {}".format(e))
  return note

def saveNotes():
  try:
    f = open(NOTES,'w')
    for line in notes:
      f.write(line)
    f.close()
  except Exception as e:
    log("Error saving notes: {}".format(e))

def loadInfo():
  info = []
  try:
    f = open(INFO,'r')
    info = f.readlines()
    f.close()
  except Exception as e:
    log("Error loading info: {}".format(e))
    return

  # Create local variables
  for line in info:
    words = line.split(' ')
    try:
      globals()[words[0]] = words[1].strip()
    except Exception as e:
      log("Couldn't load info: {}: {}".format(line,e))

def saveInfo():
  try:
    f = open(INFO,'w')
    for var in VARIABLES_TO_SAVE:
      f.write(var + ' ' + str(globals()[var]) + '\n')
    f.close()
  except FileNotFoundError as e:
    log("Failed to load info file: {}".format(e))
  except Exception as e:
    log("Failed to save info: {}".format(e))

def getName(user_id):
  for member in members:
    if member.user_id == user_id:
      return member.nickname
  log("Failed to find name of {}".format(user_id))
  return NONAME

def getMem(user_id):
  for member in members:
    if member.user_id == user_id:
      return member
  log("Failed to find member with id {}".format(user_id))

def log(message,level=1):
  if DEBUG >= level:
    print(message)

def note(message):
  notes.insert(0,message+'\n')


if __name__ == '__main__':

  # Check to see if a game is going on by reading notes

  notes = loadNotes()
  regenGame(notes)

  # Read basic info

  loadInfo()

  while True:
    retry = False
    # Initialize Basic Group infos
    try:
      group = [g for g in groupy.Group.list() if g.group_id == GROUP_ID][0]
    except Exception as e:
      log("FATAL: Could not find main group: {}:  {}".format(GROUP_ID,e))
      exit()

    # Initialize Mafia Group
    try:
      mafia_group = [g for g in groupy.Group.list() if g.group_id == MAFIA_ID][0]
    except Exception as e:
      if(GameOn):
        log("FATAL: Could not find mafia group, but game is started: {}".format(e))
        exit()
      else:
        log("Could not find old mafia group, making new group: {}".format(e))
        MAFIA_ID = groupyEP.Groups.create("MAFIA CHAT")['group_id']
        retry = True

    # Initialize Mbot
    try:
      mbot = [b for b in groupy.Bot.list() if b.bot_id == MBOT_ID][0]
    except Exception as e:
      log("Could not load mbot, will make new mbot")
      try:
        MBOT_ID = groupyEP.Bots.create("M-Bot", group.group_id, callback_url=CALLBACK_URL_MAIN)['bot']['bot_id']
        retry = True
      except Exception as e:
        log("Could not make new mbot: {}".format(e))
        try:
          if e['code'] == 400:
            log("Deleting old bots")
            for b in groupyEP.Bots.index():
              groupyEP.Bots.destroy(b['bot_id'])
              retry = True
        except:
          pass

    # Initialize Evil Mbot
    try:
      evil_mbot = [b for b in groupy.Bot.list() if b.bot_id == EVIL_MBOT_ID][0]
    except Exception as e:
      log("Could not load evil mbot, will make new evil mbot")
      try:
        EVIL_MBOT_ID = groupyEP.Bots.create("Evil M-Bot", mafia_group.group_id, callback_url=CALLBACK_URL_MAFIA)['bot']['bot_id']
        retry = True
      except Exception as e:
        log("Could not make new evil mbot: {}".format(e))
        try:
          if e['code'] == 400:
            log("Deleting old bots")
            for b in groupyEP.Bots.index():
              groupyEP.Bots.destroy(b['bot_id'])
              retry = True
        except:
          pass


    saveInfo()
    if not retry:
      break;  

  
  
  main_server = HTTPServer((ADDRESS,PORT1),MainHandler)
  if INTRO: 
    cast('RESUME',group)
    cast('RESUME',mafia_group)
  try:
#    _thread.start_new_thread(main_server.serve_forever())
#    _thread.start_new_thread(mafia_server.serve_forever())
    main_server.serve_forever()
    #mafia_server.serve_forever()
    while True:
      pass
  except KeyboardInterrupt as e:
    if OUTRO:
      cast('PAUSE',group)
      cast('PAUSE',mafia_group)
