
from newMRecord import MRecord

import pymysql.connector
from time import strftime

def getDateTime():
  return strftime("%Y-%m-%d %H:%M:%S")

# ids might just be references to objects at first!

class InsertRecord:

  def insert_fields(self, conn, fields, db):
    nameStr = ",".join(fields)
    values = []
    for field in fields:
      v = self.__dict__[field]
      if v == None:
        v = "NULL"
      elif type(v) == str:
        v = "'"+v+"'"
      elif type(v) == bool:
        v = "1" if v else "0"
      values.append(v)
    valueStr = ",".join(values)

    sql = "INSERT INTO {} ({}) VALUES ({})".format(
      db, nameStr, valueStr
    )
    with conn.cursor() as c:
      c.execute(sql)
    conn.commit()

  def findRolesetID(self, conn, roleDict, retry=False):
    """Ensure roleset exists, return roleset_id"""
    condition = " AND ".join(
      ["{}={}".format(k,roleDict[k]) for k in roleDict] +
      ["nPlayers={}".format(sum(roleDict.values()))]
    )
    sql = "SELECT roleset_id FROM Rolesets WHERE " + condition
    with conn.cursor() as c:
      c.execute(sql,())
      result = c.fetchall()

    if len(result) == 0:
      names = roleDict.keys()
      nameStr = ",".join(['n'+n for n in names])
      valueStr = ",".join(roleDict[k] for k in names)
      sql = "INSERT INTO Rolesets ({}) VALUES ({})".format(nameStr,valueStr)
      with conn.cursor() as c:
        c.execute(sql,())
      conn.commit()

      if(not retry):
        self.findRolesetID(conn, roleDict, True)
      else:
        raise Exception(
          "Failed to add roleset, unable to find after tried to add")

    elif len(result) == 1:
      return result[1]['roleset_id']
    elif len(result) >= 2:
      raise Exception("Found multiple results for a roleset")

class Game(InsertRecord):

  fields = ('g_id','winner','end_phase','end_day',
    'datetime','end_datetime','roleset_id')

  def __init__(self, g_id, roles):
    # roles is roleDict
    self.g_id = g_id
    self.winner = None
    self.end_phase = None
    self.end_day = None
    self.datetime = None
    self.end_datetime = None
    self.roles = roles
    self.roleset_id = None

  def commit(self, conn):
    self.roleset_id = self.findRolesetID(conn, self.roles)
    self.insert_fields(conn,Game.fields,"Games")    

class Vote(InsertRecord):

  fields = ('v_id','g_id','p_id1','p_id2','day','datetime')

  def __init__(self, v_id, g_id, p_id1, p_id2, day):
    self.v_id = v_id
    self.g_id = g_id
    self.p_id1 = p_id1
    self.p_id2 = p_id2
    self.day = day
    self.datetime = getDateTime()
  
  def commit(self, conn):
    self.insert_fields(conn,Vote.fields,"Votes")

class Target(InsertRecord):

  fields = ('g_id','p_id1','p_id2','night','datetime')

  def __init__(self, g_id, p_id1, p_id2, night):
    self.g_id = g_id
    self.p_id1 = p_id1
    self.p_id2 = p_id2
    self.night = night
    # Successful comes from comparing:
    #   save: compare to mtarget (and strip targets)
    #   invest: check target role and mtarget and saves and strips?
    #   milk: check mtarget and saves and strips
    #   strip: check target role
    self.datetime = getDateTime()

  def commit(self,conn):
    self.insert_fields(conn,Target.fields,"Targets")

class MTarget(InsertRecord):

  fields = ('g_id','p_id1','p_id2','night','datetime')

  def __init__(self, g_id, p_id1, p_id2, night):
    self.g_id = g_id
    self.p_id1 = p_id1
    self.p_id2 = p_id2
    self.night = night
    self.datetime = getDateTime()

  def commit(self,conn):
    self.insert_fields(conn,MTarget.fields,"MTargets")

class Reveal(InsertRecord):

  fields = ('g_id','p_id','day','distracted','datetime')

  def __init__(self, g_id, p_id, day, distracted=False):
    self.g_id = g_id
    self.p_id = p_id
    self.day = day
    self.distracted = distracted
    self.datetime = getDateTime()

  def commit(self,conn):
    self.insert_fields(conn,Reveal.fields,"Reveal")

class Guilt(InsertRecord):

  fields = ('p_id','kill_id')

  def __init__(self, p_id, kill):
    self.p_id = p_id
    self.kill = kill
    self.kill_id = None

  def commit(self, conn):
    if self.kill.k_id == None:
      #TODO: Oh noes
      pass
    self.kill_id = self.kill.kill_id
    self.insert_fields(conn, Guilt.fields, "Guilts")

class Kill(InsertRecord):

  fields = ('g_id','kill_type','p_id',
    'phase','day','successful','roleset_id','datetime')

  def __init__(self, g_id, kill_type, p_id, phase, day, successful, roles):
    self.kill_id = None 
    self.g_id = g_id
    self.kill_type = kill_type
    self.p_id = p_id
    self.phase = phase
    self.day = day
    # If someone was saved, there is still a kill
    self.successful = successful
    self.roles = roles
    self.roleset_id = None
    self.datetime = getDateTime()

  def commit(self,conn):
    self.roleset_id = self.findRolesetID(conn, self.roles)
    self.insert_fields(conn,Kill.fields,"Kills")

    sql = "SELECT LAST_INSERT_ID()"
    with conn.cursor() as c:
      c.execute(sql)
      result = c.fetchone()
    self.kill_id = result["LAST_INSERT_ID()"]


class Player(InsertRecord):

  def __init__(self, p_id, name):
    self.p_id = int(p_id)
    self.name = name

  def commit(self,conn):
    sql = "SELECT * FROM Players WHERE p_id="+str(self.p_id)
    with conn.cursor() as c:
      c.execute(sql)
      result = c.fetchone()
    if result == None:
      self.insert_fields(conn,('p_id','name'),"Players")
    else:
      if not self.name == result["name"]:
        sql = "UPDATE Players SET name={} WHERE p_id={}".format(
          "'"+self.name+"'",
          self.p_id
        )
        with conn.cursor() as c:
          c.execute(sql)
        conn.commit()

class Actor(InsertRecord):

  fields = ('g_id','p_id','role')

  def __init__(self, g_id, p_id, role):
    self.g_id = g_id
    self.p_id = p_id
    self.role = role
    
  def commit(self,conn):
    self.insert_fields(self,Actor.fields,"Actors")

class DBMRecord(MRecord):

  def __init__(self):
    self.committable = []

    self.v_id = 1

    self.mtarget = None
    self.targets = {}

    self.reveal_flag = []
    self.distracted_reveal_flag= []

  def create(self, g_id, players, roleDict):

    self.roleDict = roleDict

    self.g_id = g_id
    self.game = Game(self.g_id, dict(self.roleDict))

    for player in players:
      self.committable.append(Player(player.id,player.name))
      self.committable.append(Actor(self.g_id,player.id,player.role))

  def start(self):
    self.game.datetime = getDateTime()

  def vote(self, voter_id, votee_id, day):
    v = Vote(self.v_id, self.g_id, voter_id, votee_id, day)
    self.committable.append(v)
    self.v_id += 1

  def mafia_target(self, p_id, target_id, night):
    self.mtarget = MTarget(self.g_id, p_id, target_id, night)

  def target(self, p_id, target_id, night):
    self.targets[p_id] = Target(self.g_id, p_id, target_id, night)

  def reveal(self, p_id, day, distracted):
    if not p_id in self.reveal_flag and not (distracted and p_id in self.distracted_reveal_flag):
      r = Reveal(self.g_id, p_id, day, distracted)
      self.committable.append(r)
      if not distracted:
        self.reveal_flag.append(p_id)
      else:
        self.distracted_reveal_flag.append(p_id)

  def elect(self, voter_ids, target_id, day, roles):
    k = Kill(self.g_id, "elect", target_id, "Day", day, (not target_id == 0), roles)
    self.committable.append(k)

    for voter_id in voter_ids:
      g = Guilt(voter_id, k)
      self.committable.append(g)

  def murder(self, mafia_ids, target_id, night, successful, roles):
    k = Kill(self.g_id, "murder", target_id, "Night", night, successful, roles)
    self.committable.append(k)

    for mafia_id in mafia_ids:
      g = Guilt(mafia_id, k)
      self.committable.append(g)

  def day(self):
    self.committable.append(self.mtarget)
    self.mtarget = None

    for _, target in self.targets.items():
      self.committable.append(target)
    self.targets = {}

    self.distracted_reveal_flag = []

  def night(self):
    pass

  def end(self, winner, phase, day):
    self.game.winner = winner
    self.game.end_phase = phase
    self.game.end_day = day
    self.game.end_datetime = getDateTime()

    self.committable.append(self.game)

  def archive(self):
    conn = pymysql.connect(
      host="localhost",
      user="writer",
      password="password",
      db="MRecords",
      cursorclass=pymysql.cursors.DictCursor
    )

    for committable in self.committable:
      committable.commit(conn)

    conn.close()