#!/usr/bin/python3.4

import sys
import getopt
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer
import groupy
import json
import random
import time


### CONSTANTS ###

ADDRESS   = '0.0.0.0'
PORT      = 1121
DEBUG     = 1          # Higher means more messages
GROUP_ID  = '22287829' # TEST
MAFIA_ID  = 0 # Mafia group
COP_ID    = 0 # Cop Group
DOC_ID    = 0 # Doctor group

MBOT_ID   = '15d39f9b8fa70201b12c1dabcb'

MODERATOR = '43040067'

#GROUP_ID  =            # ADD MAFIA GROUP
#GROUP_ID  = '16143929' # SAXES
INTRO     = True
OUTRO     = True
NONAME    = ': '

ACCESS_KW = '\\'
VOTE_KW   = 'vote'
STATUS_KW = 'status'
HELP_KW   = 'help'
START_KW  = 'start'

TOWN_TEAM = 0x01
MAFIA_TEAM= 0x10
COP_RN    = 0x03
DOCTOR_RN = 0x05

GameOn = False
votes  = {}
players= {}
Time   = {'Day':0,'Time':"Day"} # Format Day Number, Day/Night
num_mafia = 0

# [Num People] : [num mafia]
GAME_COUNTS  = {
             3 : 1,
             4 : 1,
             5 : 1,
             6 : 1,
             7 : 1,
             8 : 2,
             9 : 2,
            10 : 3,
            11 : 3,
            12 : 3,
            13 : 3,
            14 : 4,
            15 : 4,
            16 : 4,
            17 : 5,
            18 : 5,
            19 : 5,
            20 : 5,
            21 : 6,
            22 : 6,
            23 : 6,
            24 : 6,
            25 : 6,
            26 : 6,
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

### Define operations ###

def vote(post):
  # Ensure Time is Day
  if not Time['Time'] == 'Day' or not GameOn:
    return False
  
  # Get voter
  try:
    voter = str(post['user_id'])
  except Exception as e:
    return False
  # Get votee
  try:
    mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
    if not len(mentions) == 1:
      return False
  except Exception as e:
    return False

  # Change vote
  votes[voter] = votee
  testKillVotes(votee)
  return True

def status(post):
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
  cast(HELP_MESSAGE)
  return True

def start(post):
  if not GameOn:
    genGame()
  return False


OPS = { VOTE_KW   : vote   ,
        STATUS_KW : status ,
        HELP_KW   : help_  ,
        START_KW  : start  ,
      }


### FILENAMES ###

NOTES     = './notes'


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
      if not OPS[words[0]](post):x
        cast("{} failed".format(words[0]))
    else:
      cast("Invalid request, (try {ACCESS_KW}{HELP_KW} for help)".format(**locals)


### HELPER FUNCTIONS ###

def testKillVotes(votee):
  # Count the number voting for votee
  count = 0
  for voter in votes:
    if (voter in players) and (voter[votes] == votee):
      count = count + 1

  # If the number of votes is in the majority
  if count > int(len(members)/2+1):
    cast("The vote to kill {} has passed".format(getName(votee)))
    if (kill(votee)):
      return True
  return False

def kill(votee):
  # Remove from players
  try:
    group.remove(getMem(votee))
    pc = players.pop(votee)
    if pc & MAFIA_TEAM > 0:
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
  Time['Time'] = 'Night'
  return True

def genGame():
  
  players = {}

  # Clear aux groups
  for mem in mafia_group:
    if not mem['user_id'] == MODERATOR:
      mafia_group.remove(mem)
  
  members = group.members()

  num_mafia = GAME_COUNTS[len(members)]

  roles = list(range(len(members)))

  random.shuffle(roles)

  for i in range(len(members)):
    if roles[i] < num_mafia:
      players[mem.user_id] = MAFIA_TEAM
    elif roles[i] == num_mafia:
      players[mem.user_id] = COP_RN
    elif roles[i] == num_mafia+1:
      players[mem.user_id] = DOC_RN
    else:
      player[mem.user_id] = TOWN_TEAM

  # add to special groups
  for player in players:
    if players[player] == MAFIA_TEAM:
      mafia_group.add(getMem(player))
    elif players[player] == COP_RN:
      cop_group.add(getMem(player))
    elif players[player] == DOC_RN:
      doc_group.add(getMem(player))
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
  return note

def saveNotes():
  try:
    f = open(NOTES,'w')
    for line in notes:
      f.write(line)
    f.close()
  except Exception as e:

def getName(user_id):
  for member in members:
    if member.user_id == user_id:
      return member.nickname
  return NONAME

def getMem(user_id):
  for member in members:
    if member.user_id == user_id:
      return member

def log(message,level=2):
  if DEBUG >= level:
    print(message)

def note(message):
  notes.insert(0,message+'\n')


if __name__ == '__main__':

  group = [g for g in groupy.Group.list() if g.group_id == GROUP_ID][0]
  mafia_group = [g for g in groupy.Group.list() if g.group_id == MAFIA_ID][0]
  members = group.members()
  mafia_members = mafia_group.members()
  mbot = [b for b in groupy.Bot.list() if b.bot_id == BOT_ID][0]

  balances = loadBalances()
  notes = loadNotes()
  kp_server = HTTPServer((ADDRESS,PORT),KPHandler)
  if INTRO: cast('MBOT IS IN THE HOUSE')
  try:
    kp_server.serve_forever()
  except:
    if OUTRO: cast('MBot out')
