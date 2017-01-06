## Test Scripts for Mafia Bot

from MInfo import *

import time

import MServer
from GroupyComm import GroupyCommTest
from MState import Preferences

def makePost(group_id,text,user_id="",mentions=[]):
  post = {}
  post['group_id'] = group_id
  post['text'] = text
  post['user_id'] = user_id
  post['attachments'] = [{'type':'mentions','user_ids':mention} for mention in mentions]
  return post

def makeDM(sender_id,text):
  DM = {}
  DM['sender_id'] = sender_id
  DM['text'] = text
  return DM

def basic_start():
  m = MServer.MServer(CommType=GroupyCommTest,restart=True)
  p = makePost(LOBBY_GROUP_ID,"/help")
  m.do_POST(p)
  return m

def get5In(m):
  ps = [makePost(LOBBY_GROUP_ID,"/in",user) for user in ["1","2","3","4","5"]]
  for p in ps:
    m.do_POST(p)
  return m

def vote(m,ver,vee):
  p = makePost(MAIN_GROUP_ID,"/vote @thum",ver, [vee])
  m.do_POST(p)
  return m

def inPlayers(m,p_id):
  for player in m.mstate.players:
    if player.id_ == p_id:
      return True
  return False


def simple_game():
  m = basic_start()
  get5In(m)
  m.mstate.startGame(["TOWN","TOWN","TOWN","TOWN","MAFIA"])
  assert m.mstate.time == "Day"
  assert m.mstate.day == 1
  vote(m,"2","1")
  vote(m,"3","1")
  vote(m,"4","1")
  assert m.mstate.time == "Night"
  assert m.mstate.day == 1
  assert not inPlayers(m,"1")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 0"))
  assert not inPlayers(m,"2")
  assert m.mstate.time == "Day"
  assert m.mstate.day == 2
  vote(m,"5","3")
  vote(m,"4","3")
  assert m.mstate.day == 0

def double_game():
  m = basic_start()
  get5In(m)
  m.mstate.startGame(["TOWN","TOWN","TOWN","TOWN","MAFIA"])
  vote(m,"2","1")
  vote(m,"3","1")
  vote(m,"4","1")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 0"))
  vote(m,"3","5")
  vote(m,"5","5")
  get5In(m)
  m.mstate.startGame(["TOWN","TOWN","TOWN","TOWN","MAFIA"])
  assert m.mstate.time == "Day"
  assert m.mstate.day == 1
  vote(m,"2","1")
  vote(m,"3","1")
  vote(m,"4","1")
  assert m.mstate.time == "Night"
  assert m.mstate.day == 1
  assert not inPlayers(m,"1")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 0"))
  assert not inPlayers(m,"2")
  assert m.mstate.time == "Day"
  assert m.mstate.day == 2
  vote(m,"5","3")
  vote(m,"4","3")
  assert m.mstate.day == 0

def cop_game():
  m = basic_start()
  get5In(m)
  m.mstate.startGame(["TOWN","COP","TOWN","TOWN","MAFIA"])
  vote(m,"2","1")
  vote(m,"3","1")
  vote(m,"4","1")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 1"))
  m.do_DM(makeDM("2","/target 2"))
  vote(m,"2","5")
  vote(m,"4","5")

def doc_game():
  m = basic_start()
  get5In(m)
  m.mstate.startGame(["TOWN","DOCTOR","TOWN","TOWN","MAFIA"])
  vote(m,"2","1")
  vote(m,"3","1")
  vote(m,"4","1")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 1"))
  m.do_DM(makeDM("2","/target 1"))
  vote(m,"2","0")
  vote(m,"3","0")
  m.do_POST(makePost(MAFIA_GROUP_ID,"/target 0"))
  m.mstate.timer_value = 2
  time.sleep(3)
  vote(m,"4","4")
  vote(m,"5","4")

def pref_game():
    m = basic_start()
    get5In(m)
    m.mstate.startGame(["TOWN","TOWN","TOWN","TOWN","MAFIA"],
                       Preferences(known_roles=True,
                                   reveal_on_death=True,
                                   kick_on_death=True))
    assert m.mstate.time == "Day"
    assert m.mstate.day == 1
    vote(m,"2","1")
    vote(m,"3","1")
    vote(m,"4","1")
    assert m.mstate.time == "Night"
    assert m.mstate.day == 1
    assert not inPlayers(m,"1")
    m.do_POST(makePost(MAFIA_GROUP_ID,"/target 0"))
    assert not inPlayers(m,"2")
    assert m.mstate.time == "Day"
    assert m.mstate.day == 2
    vote(m,"5","3")
    vote(m,"4","3")
    assert m.mstate.day == 0


if __name__ == "__main__":

  #simple_game()
  #double_game()
  #cop_game()
  #doc_game()
  pref_game()
