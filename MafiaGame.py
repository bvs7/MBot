#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer
import groupy
import groupy.api.endpoint as groupyEP
import random
import json
import _thread
import pickle

DEBUG = 1

class MafiaGame:

  """

ATTRIBUTES: ====================================================================

MAIN_GROUP_ID    The id of the group with everyone in it
mainGroup        The groupy Group object of main group

MAFIA_GROUP_ID   The id of the group with just mafia in it
mafiaGroup

playerList       List of member ids for those who are playing
savedPlayerRoles Initial roles of people. To be used in the next game
playerRoles      Dict from member ids to a string describing their role
playerVotes      Dict from member ids to member ids of who they are voting for

num_mafia        The number of mafia remaining in the game

MAIN_BOT_ID      ID of the bot that watches the main group
mainBot
MAFIA_BOT_ID     ID of the bot that watches the mafia group
mafiaBot

MODERATOR        ID of the member we have control over



time             The time of day (Day/Night)
day              Which day the game is at. 0 means no game has started

to_kill_in_morning The id of the person who the mafia chose to kill

server           The server that listens for bot posts

quit             "Stop serving and quit"


FUNCTIONS: =====================================================================

loadInfo()               Load the variables saved in the info file
checkInfo(reqList)       For each required variable in reqList, check if it is loaded

getGroup(group_id)       Find the group with the group_id.
getBot(bot_id)           Find the bot with the bot_id.

loadNotes()              Read the notes file and resume the state of the game
saveNotes()              Save the state of the game in the notes file """

  def __init__(self, i_fname, n_fname):

    self.info_fname = i_fname
    self.notes_fname = n_fname

    # Load in basic values (id values, etc)
    self.loadInfo()

    # Ensure we have all of the info we need, Create neccessary items
    self.checkInfo(['MAIN_GROUP_ID', 'MAFIA_GROUP_ID', 'MAIN_BOT_ID', 'MAFIA_BOT_ID',
                    'MODERATOR', 'ADDRESS', 'PORT'])

    # Use those values to get Groupy objects
    self.mainGroup  = self.getGroup(self.MAIN_GROUP_ID)
    self.mafiaGroup = self.getGroup(self.MAFIA_GROUP_ID)

    self.mainBot    = self.getBot(self.MAIN_BOT_ID)
    self.mafiaBot   = self.getBot(self.MAFIA_BOT_ID)

    # Create other state variables
    self.initVars()
    
    # Restore past State
    self.loadNotes()

  def run(self):

    # Setup Server
    self.server = HTTPServer((self.ADDRESS,int(self.PORT)), MainHandler)

    # Setup routing to the correct commands
    self.setupKW()

    self.quit = False

    # Run Server
    self.cast("RESUME",self.mainGroup)
    try:
      _thread.start_new_thread(self.server.serve_forever())
      # Allow edits
      while not self.quit:
        self.getCommand()
    except KeyboardInterrupt:
      pass
    self.cast("PAUSE",self.mainGroup)

  def initVars(self):
    self.time = "Day"
    self.day  = 0
    self.num_mafia = 0
    self.playerList = []
    self.savedPlayerList = {}
    self.playerRoles = {}
    self.playerVotes = {}
    self.to_kill_in_morning = ""

    self.MAFIA_ROLES = [ "MAFIA" ]
    self.TOWN_ROLES  = [ "TOWN", "COP", "DOCTOR" ]

    self.ROLE_EXPLAIN= {
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
                 "survive.")
      }

  def getCommand(self):
    i = input()
    if i in ["q","quit"]:
      self.quit = True
    eval(i)

### INIT HELPER FUNCTIONS ######################################################

  def loadInfo(self):
    try:
      f = open(self.info_fname,'r')
      lines = f.readlines()
      f.close()
    except Exception as e:
      self.log("Error loading info: {}".format(e))
      return False

    for line in lines:
      words = line.split()
      if len(words) == 2:
        self.__dict__[words[0]] = words[1]
      else:
        self.log("Couldn't load a line: {}".format(words))
    return True

  def checkInfo(self,reqList):
    for req in reqList:
      if not req in dir(self):
        self.log("Do not have required info: {}".format(req))
        exit() # FOR NOW
    return True

  def getGroup(self,group_id):
    try:
      groups = [g for g in groupy.Group.list() if g.group_id == group_id]
    except Exception as e:
      self.log("Failed to load group from id {}: {}".format(group_id,e))
      exit() # FOR NOW
    if len(groups) >= 1:
      return groups[0]
    else:
      self.log("No group found with id {}".format(group_id))

  def getBot(self,bot_id):
    try:
      bots = [b for b in groupy.Bot.list() if b.bot_id == bot_id]
    except Exception as e:
      self.log("Failed to load bot from id {}: {}".format(bot_id,e))
      exit() # FOR NOW
    if len(bots) >= 1:
      return bots[0]
    else:
      self.log("No bot found with id {}".format(bot_id))

  def loadNotes(self):    
    try:
      self = pickle.load(open(self.notes_fname,"rb"))
    except Exception as e:
      self.log("Error loading notes: {}".format(e))
      return False
    return True

  def saveNotes(self):
    # Save Notes using pickle, or json? Json makes them editable
    # We'll try pickle for now.
    try:
      pickle.dump( self, open(self.notes_fname,"wb"))
    except Exception as e:
      self.log("Failed to save notes: {}".format(e))
      return False
    return True

### POST FUNCTIONS #############################################################


### VOTE -----------------------------------------------------------------------
      
  def vote(self,post,words):
    """{}{} @[player]  - Vote for someone. Once they have a majority of votes they are killed"""
    self.log("VOTE")
    # Assert time is day
    if not self.time == "Day" or self.day == 0:
      self.log("Vote Failed: not Day")
      return False
    # Get voter
    try:
      voter = post['user_id']
    except Exception as e:
      self.log("Vote failed: couldn't get voter: {}".format(e))
      return False
    # Get votee
    try:
      mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
      if not len(mentions) <= 1:
        self.log("Vote Failed: invalid votee count: {}".format(len(mentions)))
        return False
      elif words[1].lower() == "me":
        votee = voter
      elif words[1].lower() == "none":
        if voter in self.playerVotes: del self.playerVotes[voter]
        self.log("Retracted Vote {}".format(voter))
        self.cast("Vote retraction successful",self.mainGroup)
        return True
      else:
        votee = mentions[0]['user_ids'][0]
    except Exception as e:
      self.log("Vote Failed: Couldn't get votee: {}".format(e))
      return False
    # Ensure vote is not for moderator
    if votee == self.MODERATOR:
      self.log("Vote failed: Tried to vote for Moderator")
      self.cast("HOW DARE YOU",self.mainGroup)
      return False
    # Check that votee is in game
    if not votee in self.playerList:
      self.log("Vote Failed: votee not playing")
      return False
    # Change vote
    self.playerVotes[voter] = votee
    self.log("Vote succeeded: {} changed vote to {}".format(voter,votee))
    self.testKillVotes(votee)
    return True

  def status(self,post={},words=[]):
    """{}{}  - Check the status of the game"""
    self.log("STATUS")
    reply = "It is {} {}\n".format(self.time,self.day)
    if self.day == 0:
      # Display who will be in the game
      reply = reply + "Players: (use /in to join)"
      for player in self.playerList:
        reply = reply + "\n" + self.getName(player)
    else:
      # Output players and who is voting for who
      reply = reply + "[Alive]:[Votes]\n"
      for player in self.playerList:
        if not player == self.MODERATOR:
          reply = reply + self.getName(player) + " : "
          count = 0
          for voter,votee in self.playerVotes.items():
            if(votee == player):
              count = count + 1
              reply = reply + self.getName(voter)+" "
          reply = reply + str(count) +  "\n"
    self.cast(reply,self.mainGroup)
    return True

  def help_(self,post={},words=[]):
    """{}{}  - Display this message"""
    self.cast(self.HELP_MESSAGE,self.mainGroup)
    return True

  def start(self,post={},words=[]):
    """{}{}  - Start a game with the current players"""
    # NOTE: When the day is 0, the following is true:
    if self.day == 0:
      return self.startGame()
      
    return False

  def in_(self,post,words=[]):
    """{}{}  - Join the next game"""
    self.log("IN")
    # Ensure the game hasn't started
    if not self.day == 0:
      self.log("In failed: game has started")
      return False
    # Get inquirer
    try:
      player = post['user_id']
    except Exception as e:
      self.log("In failed: couldn't get voter: {}".format(e))
      return False
    # Add to list
    if player not in self.playerList:
      self.playerList.append(player)
      self.cast("{} added to game".format(self.getName(player)),self.mainGroup)
    return True

  def out(self,post,words=[]):
    """{}{}  - Leave the next game"""
    self.log("OUT")
    # Ensure the game hasn't started
    if not self.day == 0:
      self.log("Out failed: game has started")
      return False
    # Get player
    try:
      player = post['user_id']
    except Exception as e:
      self.log("Out failed: couldn't get voter: {}".format(e))
      return False
    # try to remove from list:
    if player in self.playerList: self.playerList.remove(player)
    self.cast("{} removed from game".format(self.getName(player)),self.mainGroup)
    return True


  ### MAFIA POST FUNCTIONS #####################################################

  def mafia_help(self,post={},words=[]):
    """{}{}  - Display this message"""
    self.cast(self.M_HELP_MESSAGE,self.mafiaGroup)
    return True

  def mafia_kill(self,post,words):
    """{}{} [number]  - Kill the player associated with this number (from options)"""
    try:
      player = self.playerList[int(words[1])]
      if(self.kill(player)):
        if(not self.day == 0):
          self.cast("It is done",self.mafiaGroup)
          self.toDay()
          return True
    except Exception as e:
      self.log("Mafia kill failed: {}".format(e))
    return False
    
  def mafia_displayOptions(self,post={},words=[]):
    """{}{}  - List the options to kill and the numbers to use to kill them"""
    r = ""
    c = 0
    for player in self.playerList:
      r = r + str(c) + ": " + self.getName(player) + "\n"
      c = c + 1
    r = r + str(c) + ": No kill"
    self.cast(r,self.mafiaGroup)
    return True

  def setupKW(self):
    # OP KEYWORDS
    self.ACCESS_KW = '/'
    
    VOTE_KW   = 'vote'
    STATUS_KW = 'status'
    HELP_KW   = 'help'
    START_KW  = 'start'
    IN_KW     = 'in'
    OUT_KW    = 'out'

    KILL_KW   = 'kill'
    OPTS_KW   = 'options'
    
    # This dict routes the command to the correct function
    self.OPS ={ VOTE_KW   : self.vote   ,
                STATUS_KW : self.status ,
                HELP_KW   : self.help_  ,
                START_KW  : self.start  ,
                IN_KW     : self.in_    ,
                OUT_KW    : self.out    ,
              }

    self.MOPS={ HELP_KW   : self.mafia_help ,
                KILL_KW   : self.mafia_kill ,
                OPTS_KW   : self.mafia_displayOptions,
              }
                

    # Setup help message
    h = "Welcome to the Mafia Groupme.\nHere are some commands to use:\n"
    for command,fun in self.OPS.items():
      h = h + "\n" + fun.__doc__.format(self.ACCESS_KW,command)

    self.HELP_MESSAGE = h

    # Setup Mafia help message
    h = "Welcome to the private MAFIA CHAT. You can discuss covert matters here.\nAlso, use these commands:"
    for command,fun in self.MOPS.items():
      h = h + "\n" + fun.__doc__.format(self.ACCESS_KW,command)

    self.M_HELP_MESSAGE = h

### POST HELPER FUNCTIONS ######################################################

  def testKillVotes(self,votee):
    # Get people voting for votee
    voters = [v for v,vee in self.playerVotes.items() if vee == votee]
    # If the number of votes is in the majority, kill
    num_players = len(self.playerList)
    if len(voters) > num_players/2:
      self.cast("The vote to kill {} has passed".format(
                self.getName(votee)),self.mainGroup)
      if (self.kill(votee)):
        if not self.day == 0:
          self.toNight()
        return True
    else:
      self.cast("Vote successful: {} more vote{}until {} is killed".format(
           int((num_players)/2+1)-len(voters),
           " " if int((num_players)/2+1)-len(voters) == 1 else "s ",
           self.getName(votee) ) ,self.mainGroup)
      return True

  def kill(self,votee):
    if self.time == "Night":
      if votee in self.playerList:
        self.to_kill_in_morning = votee
        return True
    # Remove from players things
    try:
      role = self.playerRoles.pop(votee)
      if role in self.MAFIA_ROLES:
        self.num_mafia = self.num_mafia - 1
      self.playerList.remove(votee)
      if votee in self.playerVotes: del self.playerVotes[votee]
    except Exception as e:
      self.log("Failed to kill {}: {}".format(votee,e))
      return False
    # Check win conditions
    if self.num_mafia == 0:
      self.cast("TOWN WINS",self.mainGroup)
      self.endGame()
    if self.num_mafia >= len(self.playerList)/2:
      self.cast("MAFIA WINS",self.mainGroup)
      self.endGame()
    return True

  def gameNumbers(self,num_players):
    # This could eventually return other things, like the number of masons etc
    # [Num People] : [num mafia]
    GAME_COUNTS  = {
       3 : 1,  4 : 1,  5 : 1,  6 : 1,  7 : 1,  8 : 2,  9 : 2,  10 : 3,
      11 : 3,  12 : 3, 13 : 3, 14 : 4, 15 : 4, 16 : 4, 17 : 5, 18 : 5,
      19 : 5,  20 : 5, 21 : 6, 22 : 6, 23 : 6, 24 : 6, 25 : 6, 26 : 6,
      27 : 6, }
    return GAME_COUNTS[num_players]

  def startGame(self):
    self.day = 1
    self.time = "Day"
    # Assign Roles
    num_players = len(self.playerList)
    self.num_mafia = self.gameNumbers(num_players)
    # First shuffle for assignment
    random.shuffle(self.playerList)
    c = 0
    for player in self.playerList:
      if c < self.num_mafia:
        self.playerRoles[player] = "MAFIA"
#      elif c == self.num_mafia:
#        self.playerRoles[player] = "COP"
#      elif c == self.num_mafia + 1:
#        self.playerRoles[player] = "DOCTOR"
      else:
        self.playerRoles[player] = "TOWN"
      c = c + 1
      self.log("{} {}".format(self.getName(player),self.playerRoles[player]))
    # Save players and roles
    self.savedPlayerRoles = self.playerRoles.copy()
    # Shuffle again for anonymity
    random.shuffle(self.playerList)
    # Send out private messages with roles
    for player,role in self.playerRoles.items():
      groupyEP.DirectMessages.create(player,self.ROLE_EXPLAIN[role])
      if role in self.MAFIA_ROLES:
        self.mafiaGroup.add({'user_id':player})
    # Send out group messages
    self.cast(("Dawn. Of the game and of this new day. You have all learned "
               "that scum reside in this town. A scum that you must purge. "
               "Kill someone!"), self.mainGroup)
    return True
    
  def endGame(self):
    self.day = 0
    self.time = "Day"
    self.playerVotes.clear()
    self.playerRoles.clear()
    # Remove all from Mafia Group
    self.mafiaGroup.refresh()
    for mem in self.mafiaGroup.members():
      if not mem.user_id == self.MODERATOR:
        self.mafiaGroup.remove(mem)
        self.log("removing {} from mafia chat".format(mem.nickname))
    # Refresh the old members, also reveal roles
    r = "GG, here were all the roles:"    
    self.playerList = []
    for player,role in self.savedPlayerRoles.items():
      r = r + "\n" + self.getName(player) + ": " + role
      self.playerList.append(player)
    self.cast(r,self.mainGroup)
    return True

  def toDay(self):
    self.time = "Day"
    self.day = self.day + 1
    self.cast("Uncertainty dawns, as does this day",self.mainGroup)
    if not self.to_kill_in_morning == "":
      if self.kill(self.to_kill_in_morning):
        self.cast("Tragedy has struck! {} is dead! Someone must pay for this!\
                  Vote to kill somebody!".format(self.getName(self.to_kill_in_morning)),
                  self.mainGroup)

  def toNight(self):
    self.time = "Night"
    self.playerVotes.clear()
    self.cast("Night falls and everyone sleeps",self.mainGroup)
    self.cast("As the sky darkens, so too do your intentions. Pick someone to kill",
              self.mafiaGroup)
    self.mafia_displayOptions()

  def getName(self,player_id):
    self.mainGroup.refresh()
    members = self.mainGroup.members()
    for m in members:
      if m.user_id == player_id:
        return m.nickname
    return "__"

  def log(self,message,level=1):
    if DEBUG >= level:
      print(message)

  def cast(self,message,group):
    try:
      groupyEP.Messages.create(group.group_id,message)
      self.log("CAST-{}: {}".format(group.name,message))
      return True
    except Exception as e:
      self.log("FAILED TO CASE-{} {}: {}".format(group.name,message,e))
      return False

  def do_POST(self,post):
    if(  post['group_id'] == self.MAIN_GROUP_ID): self.do_POST_MAIN(post)
    elif(post['group_id'] == self.MAFIA_GROUP_ID): self.do_POST_MAFIA(post)
    self.saveNotes()
    
  def do_POST_MAIN(self,post):
    self.log("Got POST in MAIN")
    # Test if we need to do anything
    try:
      if(post['text'][0:len(self.ACCESS_KW)] == self.ACCESS_KW):
        self.log("Is Access")
        words = post['text'][len(self.ACCESS_KW):].split() 
        if(not len(words) == 0 and words[0] in self.OPS):
          self.log("Type: {}".format(words[0]))
          if not self.OPS[words[0]](post,words):
            self.cast("{} failed".format(words[0]),self.mainGroup)
        else:
          self.cast("Invalid request, (try {}{} for help)".format(self.ACCESS_KW,"help"),
                    self.mainGroup)
    except KeyError as e: pass

  def do_POST_MAFIA(self,post):
    self.log("Got POST in MAFIA")
    # Test if we need to do anything
    try:
      if(post['text'][0:len(self.ACCESS_KW)] == self.ACCESS_KW):
        self.log("Is Access")
        words = post['text'][len(self.ACCESS_KW):].split() 
        if(not len(words) == 0 and words[0] in self.MOPS):
          self.log("Type: {}".format(words[0]))
          if not self.MOPS[words[0]](post,words):
            self.cast("{} failed".format(words[0]),self.mainGroup)
        else:
          self.cast("Invalid request, (try {}{} for help)".format(self.ACCESS_KW,"help"),
                    self.mainGroup)
    except KeyError as e: pass

### MainHandler ###############################################################
class MainHandler(BaseHandler):
  def do_POST(self):
    try:
      #get contents of the POST
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except Exception as e:
      post = {}

    do_POST_ALL(post)
    return

    self.saveNotes()

def do_POST_ALL(post):
  global m
  m.do_POST(post)

if __name__ == '__main__':

  global m

  m = MafiaGame("info","notes")

  m.run()
