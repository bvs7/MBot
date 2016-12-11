#!/usr/bin/python3

# Base Classes for each required class. These are implemented as test classes

class BaseGroupyComm:

  def __init__(self):
    log("BaseGroupyComm Init",0)
    self.mainGroupId = 1
    self.lobbyGroupId = 2
    self.mafiaGroupId = 3

    self.main = []
    self.mafia = []

  def cast(self,msg,group_id=1):
    log("BaseGroupyComm cast",0)
    m = "CAST: "
    if group == self.mainGroup:
      m += "(MAIN) "
    elif group == self.mafiaGroup:
      m += "(MAFIA) "
    elif group == self.lobbyGroup:
      m += "(LOBBY) "
    m += msg

    log(m,1)

  def sendDM(self,msg,player_id):
    log("BaseGroupyComm sendDM",0)
    log("DM: "+"("+player_id+") "+msg)

  def getDMs(self,player_id):
    log("BaseGroupyComm getDMs",0)
    return []

  def getName(self,player_id):
    log("BaseGroupyComm getName",0)
    return "[Name of {}]".format(player_id)

  def getMembers(self):
    log("BaseGroupyComm getMembers",0)
    print("Getting Members")
    return []

  def addMafia(self, player_id):
    log("BaseGroupyComm addMafia",0)
    self.mafia.append(player_id)

  def clearMafia(self):
    log("BaseGroupyComm clearMafia",0)
    self.mafia.clear()

  def addMain(self, player):
    log("BaseGroupyComm addMain",0)
    if not player in self.main:
      self.main.append(player)

  def clearMain(self, saveList = []):
    log("BaseGroupyComm clearMain",0)
    for p in self.main:
      if not p in saveList:
        self.main.remove(p)

  def remove(self, p_id):
    log("BaseGroupyComm remove",0)
    if p_id in self.main:
      self.main.remove(p_id)
    if p_id in self.mafia:
      self.mafia.remove(p_id)
      

  def intro(self):
    log("intro")

  def outro(self):
    log("outro")


class BaseMState:

  def __init__(self):
    pass

  def vote(self,voter_id,votee_id):
    log("BaseMState vote",0)

  def mafiaTarget(self,opt):
    log("BaseMState mafiaTarget",0)

  def mafia_options(self):
    log("BaseMState mafia_options",0)

  def target(self,p,opt):
    log("BaseMState target",0)

  def send_options(self,prompt,p):
    log("BaseMState send_options",0)

  def reveal(self,p):
    log("BaseMState reveal",0)

  def startGame(self):
    log("BaseMState startGame",0)

  def setTimer(self):
    log("BaseMState setTimer",0)

class BaseMServer:

  def __init__(self):
    pass

  def do_POST(self,post):
    pass

  def do_DM(self,DM):


def makePost(group_id,text,user_id="",mentions=[]):
  post = {}
  post['group_id'] = group_id
  post['text'] = text
  post['user_id'] = user_id
  post['attachments'] = [{'type':'mentions','user_ids':mention} for mention in mentions]
  return post  
