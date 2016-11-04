# Main info module

import json  # For loading vars

DEBUG = 2
SILENT = False

info_fname = "info"

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
    return json.load( open(NOTES_FNAME+'/'+varName,'r') )
  except Exception as e:
    log("Falied to load {}: {}".format(varName,e))
    raise NoteError(str(e)+": "+varName)

def saveNote(var,name):
  """Saves a variable"""
  try:
    json.dump(var, open(self.NOTES_FNAME+'/'+name,'w'))
  except Exception as e:
    log("Failed to save {}: {}".format(name, e))
    raise NoteError(str(e)+": "+name)


### DATA FOR MSTATE #############

MAFIA_ROLES = [ "MAFIA" ]
TOWN_ROLES  = [ "TOWN", "COP", "DOCTOR", "IDIOT" ]

ROLE_EXPLAIN= {
  "MAFIA" : ("You are MAFIA. You are now part of the mafia chat to talk "
             "privately with your co-conspirators. During the day, try not "
             "to get killed. During the Night, choose somebody to kill!"),
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
  }

# ROLE GENERATION

BASE_SCORE = -8

ROLE_SCORES = {
  "MAFIA"  : -3,
  "DOCTOR" :  4,
  "COP"    :  4,
  "TOWN"   :  2,
  "IDIOT"  : -2,
}

# Probability of town roles being chosen
TOWN_WEIGHTS = [
  ["TOWN", "DOCTOR", "COP"],
  [75,     10,       10]
]

# Probability of anti-town roles being chosen
MAFIA_WEIGHTS = [
  ["MAFIA", "IDIOT"],
  [85,      20],
]
