#!/usr/bin/python3

import sys
import getopt
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer
import groupy
import json
import random
import time

### ADMINISTRATIVE CONSTANTS ###

DEBUG = 1


### CONSTANTS ###

ADDRESS   = '0.0.0.0'
PORT      = 1121
GROUP_ID  = '22287829' # TEST
MAFIA_ID  = 0 # Mafia group

CALLBACK_URL_MAIN  = 'http://24.59.62.95:1121'
CALLBACK_URL_MAFIA = 'http://24.59.62.95:1122'

MBOT_ID   = '15d39f9b8fa70201b12c1dabcb'

MODERATOR = '43040067'

INTRO     = True
OUTRO     = True
NONAME    = ': '

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
GAME_COUNTS  = { 3 : 1,  4 : 1,  5 : 1,  6 : 1,  7 : 1,  8 : 2,  9 : 2,  10 : 3,
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
LOG       = './log'

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
  cast(reply)
  return True

def help_(post):
  log("Help")
  cast(HELP_MESSAGE)
  return True

def start(post):
  log("Start")
  if not GameOn:
    genGame()
  return False

# This dict routes the command to the correct function
OPS = { VOTE_KW   : vote   ,
        STATUS_KW : status ,
        HELP_KW   : help_  ,
        START_KW  : start  ,
      }


### HANDLER ###

class MHandler(BaseHandler):
  
  def do_POST(self):
    try:
      # Get contents of the POST
      length = int(self.headers['Content-length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except KeyError as e:
      post = {}
    except ValueError as e:
      post = {}
      
    # Test if we need to do anything
    try:
      if(post['text'][0:len(ACCCESS_KW)] == ACCESS_KW):
        words = post['text'][len(ACCESS_KW):].split()
    except KeyError as e:
      return

    if(words[0] in OPS):
      if not OPS[words[0]](post):
        cast("{} failed".format(words[0]))
    else:
      cast("Invalid request, (try {ACCESS_KW}{HELP_KW} for help)".format(**locals))


### HELPER FUNCTIONS ###

def testKillVotes(votee):
  # Get people voting for votee
  voters = [v for v in votes if votes[v] == votee]
  
  # If the number of votes is in the majority, kill
  if len(voters) > int(len(members)/2):
    cast("The vote to kill {} has passed".format(getName(votee)))
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
    return False
  # Check win conditions
  if num_mafia == 0:
    GameOn = False
    cast("TOWN WINS")
    return True
  if num_mafia >= (len(players))/2:
    GameOn = False
    cast("MAFIA WINS")
    return True
  return True

def genGame():
  
  players = {}

  # Clear aux groups
  for mem in mafia_group:
    if not mem['user_id'] == MODERATOR:
      mafia_group.remove(mem)

  # Refresh Members in the group
  members = group.members()
  # Find how many mafia there should be
  num_mafia = GAME_COUNTS[len(members)]
  # Randomly order members
  roles = list(range(len(members)))
  random.shuffle(roles)

  # Assign roles
  for i in range(len(members)):
    if roles[i] < num_mafia: # First few are mafia
      players[mem.user_id] = "MAFIA"
    elif roles[i] == num_mafia: # Then cop
      players[mem.user_id] = "COP"
    elif roles[i] == num_mafia+1: # Then Doc
      players[mem.user_id] = "DOCTOR"
    else:
      player[mem.user_id] = "TOWN"

  # add to special groups
  for player in players:
    if players[player] == MAFIA_TEAM:
      mafia_group.add(getMem(player))
      
  GameOn=True
  Time = {'Day' : 1, 'Time' : 'Day'}

  cast("The game has started! There are {} people total and {} mafia.\
        It is the dawn of the first day! Kill someone!")
  
  
def cast(message, bot = mbot):
  bot.post(message)

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

  # Initialize Basic Group infos
  try:
    group = [g for g in groupy.Group.list() if g.group_id == GROUP_ID][0]
  except Exception as e:
    log("Could not find main group, fatal: {}".format(e))
    exit()

  # Initialize Mafia Group
  try:
    mafia_group = [g for g in groupy.Group.list() if g.group_id == MAFIA_ID][0]
  except Exception as e:
    if(GameOn):
      log("Could not find mafia group, but game is started, fatal: {}".format(e))
      exit()
    else:
      log("Could not find old mafia group, making new group: {}".format(e))
      mafia_group = groupy.Groups.create("MAFIA CHAT")['group_id']

  try:
    mbot = [b for b in groupy.Bot.list() if b.bot_id == BOT_ID][0]
  except Exception as e:

  m_server = HTTPServer((ADDRESS,PORT),MHandler)
  if INTRO: cast('MBOT IS IN THE HOUSE')
  try:
    kp_server.serve_forever()
  except:
    if OUTRO: cast('MBot out')
