# Main info module

import pickle  # For loading vars
import os

DEBUG = 2
SILENT = False

info_fname = "info"

### TIMING ##########

SET_TIMER_VALUE = 5*60

try:
  f = open(info_fname,'r')
  lines = f.readlines()
  f.close()
except Exception as e:
  print("Error loading info: {}".format(e))

for line in lines:
  words = line.split()
  if len(words) == 2:
    globals()[words[0]] = words[1]
  else:
    print("Couldn't load a line: {}".format(words))

def log(msg, debug=2):
  if DEBUG >= debug:
    print(msg)

class NoteError(Exception):
  def __init__(self,msg):
    self.msg = msg

def loadNote(varName):
  """Loads and returns a variable from a file"""
  try:
    return pickle.load( open(NOTES_FNAME+'/'+varName,'rb') )
  except Exception as e:
    log("Falied to load {}: {}".format(varName,e))
    raise NoteError(str(e)+": "+varName)

def saveNote(var,name):
  """Saves a variable"""
  fname = NOTES_FNAME + "/" + name
  if not os.path.exists(NOTES_FNAME):
    os.makedirs(NOTES_FNAME)
  try:
    pickle.dump(var, open(fname,'wb'))
  except Exception as e:
    log("Failed to save {}: {}".format(name, e))
    raise NoteError(str(e)+": "+name)


### DATA FOR MSTATE #############

MAFIA_ROLES = [ "MAFIA" , "GODFATHER"]
TOWN_ROLES  = [ "TOWN", "COP", "DOCTOR", "IDIOT" ]

ROLE_EXPLAIN= {
  "MAFIA" : ("You are MAFIA. You are now part of the mafia chat to talk "
             "privately with your co-conspirators. During the day, try not "
             "to get killed. During the Night, choose somebody to kill!"),
  "GODFATHER" : ("You are a GODFATHER. You are a leader of the mafia, up "
                 "to no good! Use the mafia chat to conspire. If a cop "
                 "investigates you, they'll see you as TOWN!"),
  "TOWN"  : ("You are TOWN. You are a normal player in this game, the last "
             "line of defense against the mafia scum. Sniff out who the "
             "mafia are and convince your fellow town members to kill them "
             "during the day!"),
  "COP"   : ("You are a COP. You are one of the most powerful members of "
             "the townspeople. During the night, send a direct message to me "
             "with the number of the person you want to investigate, and "
             "upon morning, I will tell you whether that person is town or "
             "mafia."),
  "DOCTOR": ("You are a DOCTOR. Your job is to save the townspeople from "
             "the mafia scum. During the night, send a direct message to me"
             " with the number of the person you want to save. If the mafia"
             " targets them, they will have a near death experience, but "
             "survive."),
  "IDIOT" : ("You are the villiage IDIOT. Your life's dream is to be such an"
             " annoyance that the townsfolk kill you in frustration. You don't"
             " care whether the mafia win or lose, as long as you get votes."),
  "CELEB" : ("You are a CELEBrity. Everybody knows who you are, they just "
             "don't recognize you right now. You can reveal yourself during Day "
             "by sending me '/reveal'. But be careful! You'll be quite the "
             "target once you do this!")
  }

SAVES = [
      "time","day","num_mafia","mafia_target","players","nextPlayerIDs", 
      "idiot_winners", "savedRoles", "timer_value", "timerOn"
    ]

# ROLE GENERATION

BASE_SCORE = -8

ROLE_SCORES = {
  "MAFIA"  : -3,
  "GODFATHER" : -3,
  "DOCTOR" :  4,
  "COP"    :  4,
  "TOWN"   :  2,
  "IDIOT"  : -2,
  "CELEB"  :  3,
}

# Probability of town roles being chosen
TOWN_WEIGHTS = [
  ["TOWN", "DOCTOR", "COP", "CELEB"],
  [75,     15,       15,    10]
]

# Probability of anti-town roles being chosen
MAFIA_WEIGHTS = [
  ["MAFIA", "IDIOT", "GODFATHER"],
  [85,      15,       10],
]


# OP KEYWORDS
ACCESS_KW = '/'

START_KW  = 'start'
IN_KW     = 'in'
OUT_KW    = 'out'
WATCH_KW  = 'watch'

VOTE_KW   = 'vote'
STATUS_KW = 'status'
HELP_KW   = 'help'
TIMER_KW  = 'timer'

TARGET_KW = 'target'
OPTS_KW   = 'options'

REVEAL_KW = 'reveal'

RESTART_KW= 'restart'

## HELP MESSAGES

L_HELP_MESSAGE=("Welcome to the Mafia Groupme. This is the Lobby\n"
                "To join a game, use /in. To start the game, /start\n"
                "If you change your mind, use /out to leave the next game\n"
                "To check the status of a current game, use /status\n"
                "For this help message, try /help\n")

HELP_MESSAGE =("Welcome to the Mafia Groupme. "
               "In this Groupme you can play mafia via certain commands.\n"
               "/vote @  - Use this to vote for somebody, where @ is a mention. "
               "You can also use /vote me to vote yourself, /vote none to cancel "
               "And /vote nokill to vote for no kill.\n"
               "/status  - Get the current state of the game\n"
               "/help  - Display this message\n"
               "/timer  - Set a five minute time limit on the current day\n")

M_HELP_MESSAGE = ("Hey you naughty people, here is what you can do here:\n"
                  "/options  - Display the list of what numbers to use to kill.\n"
                  "/target #  - Kill the person who is option #. For example, if "
                  "Brian is option 2, enter '/target 2'\n"
                  "/help  - Display this message.")

DOC_HELP_MESSAGE = ("Hey Doc, here is what you can do here:\n"
                    "/options  - Display the list of what numbers to use to save.\n"
                    "/target #  - Save the person who is option #. For example, if "
                    "Brian is option 2, enter '/target 2'\n"
                    "/help  - Display this message.")

COP_HELP_MESSAGE = ("Hey Cop, here is what you can do here:\n"
                    "/options  - Display the list of what numbers to use to search.\n"
                    "/target #  - Search the person who is option #. For example, if "
                    "Brian is option 2, enter '/target 2'\n"
                    "/help  - Display this message.")

CELEB_HELP_MESSAGE = ("Hey Celeb, here is what you can do here:\n"
                      "/reveal  - MODERATOR will send a message to the main group "
                      " confirming you as town. You can use this whenever you want")

DM_HELP_MESSAGE = ("In the Main Groupme you can play mafia via these commands:\n"
                   "/vote @  - Use this to vote for somebody, where @ is a mention. "
                   "You can also use /vote me to vote yourself, /vote none to cancel "
                   "And /vote nokill to vote for no kill.\n"
                   "/status  - Get the current state of the game. You can also "
                   "enter this command here to privately get the stats\n"
                   "/help  - Display this message\n"
                   "/in  - Be in the NEXT game. During a game, this means the game "
                   "after this one finishes.\n"
                   "/out  - If you change your mind, use this to get out of the "
                   "next game.\n"
                   "/start  - Use this to begin a game with those who have enrolled.\n")
