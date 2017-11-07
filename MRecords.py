# Used to analyze records
from MInfo import *
import os

''' In player_records, there are folders with player_ids with the following info:
    roles: The number of times this player has been each role and the number
        of times winning as that role vs losing as that role
    # A folder for every other player this player has interacted with that contains:
    #     votes: Number of times voting for that person for each possible tuple of
    #         (my_role, your_role)
    #     target: Number of times targeting that person for each (my_role,your_role)
    #     mtarget: Number of times your mafia targeted the other.
'''

class Event:
    """ An event in a GameRec. These have a type and some clarifying values
        e_types     active      passive     detail
        START       players     None        (game_num, rules)
        VOTE        voter       votee       ...
        DECIDE      voters      victim      ...
        KILL        (live)mafia victim      ...
        TARGET      actor       target      ...
        WIN         winners     losers      (alive,winning_team)
        REVEAL      revealer    None        (day,time,n_players)
        """

    def __init__(self, e_type, active, passive, detail):
        self.e_type = e_type
        self.active = active
        self.passive = passive
        self.detail = detail

class GameRec:
    """ The records of a game. Contains all info needed to record things
        I'm going to try to implement this in an event format, so everything
        that happens in a game is an event and those events can be read through
        to get all stats """

    def __init__(self, game_records):
        ''' game_records is a string representing the output of the game '''

        self.events = [] # A list of events

        # record reading temp data
        state = "I"

        # Game State data:
        rules = {} # List of game rules
        og_players = {}
        players = {} # Mapping of p_ids to roles
        votes = {} # Mapping from voter to votee
        targets = {}
        mtarget = None
        time = ""
        day = 0
        game_num = 0

        ### START INTERPRETING DATA

        for line in game_records:
            if line == "":
                return
            tokens = line.split()
            if state == "I":
                if tokens[0] == 'CREATE':
                    game_num = int(tokens[1])
                    state = "RULES"
            elif state == "RULES":
                if tokens[0] == 'ROLES:':
                    state = "ROLES"
                else:
                    rules[tokens[0][:-1]] = tokens[1]
            elif state == "ROLES":
                if tokens[0] == "START":
                    self.events.append(Event(
                        'START',
                        [(p_id,role) for p_id,role in players.items()],
                        None,
                        (game_num,rules) )
                    )
                    state = "GAME"
                elif tokens[0] == "NIGHT":
                    if tokens[0] == "NIGHT":
                        time = 'NIGHT'
                        day = int(tokens[1])
                    else:
                        time = 'DAY'
                        day = 1
                else:
                    players[tokens[0]] = tokens[1]
                    og_players[tokens[0]] = tokens[1]

            elif state == "GAME":
                if tokens[0] == "SAVED":
                    continue
                if tokens[1] == "WINS":
                    if tokens[0] == "TOWN":
                        self.events.append(Event(
                            'TOWN_WIN',
                            [(p_id,role) for p_id,role in og_players.items() if role in TOWN_ROLES],
                            [(p_id,role) for p_id,role in og_players.items() if role in MAFIA_ROLES],
                            [(p_id,role) for p_id,role in players.items()]
                        ))
                    elif tokens[0] == "MAFIA":
                        self.events.append(Event(
                            'MAFIA_WIN',
                            [(p_id,role) for p_id,role in og_players.items() if role in MAFIA_ROLES],
                            [(p_id,role) for p_id,role in og_players.items() if role in TOWN_ROLES],
                            [(p_id,role) for p_id,role in players.items()]
                        ))
                    return
                if time == 'NIGHT':
                    if tokens[0] == 'TARGET':
                        targets[tokens[1]] = tokens[3]
                    elif tokens[0] == 'MTARGET':
                        mtarget = tokens[1]
                    elif tokens[0] == 'KILL':
                        # Time to go to day in a bit?
                        self.events.append(Event(
                            'KILL',
                            [(p_id,role) for p_id,role in players.items() if role in MAFIA_ROLES],
                            (tokens[1], tokens[2]),
                            None
                        ))

                        del players[tokens[1]]

                    elif tokens[0] == 'DAY':
                        for actor,target in targets.items():
                            if actor in players and target in players:
                                self.events.append(Event(
                                    'TARGET',
                                    (actor,players[actor]),
                                    (target,players[target]),
                                    'SAVED' if players[actor] == "DOCTOR" and target == mtarget else None
                                ))
                        targets = {}
                        mtarget = None
                        time = 'DAY'
                        day = int(tokens[1])
                elif time == 'DAY':
                    if tokens[0] == 'VOTE':
                        votes[tokens[1]] = tokens[3]
                    elif tokens[0] == 'REVEAL':
                        revealed = False
                        for event in self.events:
                            if event.e_type == "REVEAL" and event.active == tokens[1]:
                                revealed = True
                        if not revealed:
                            self.events.append(Event(
                                'REVEAL',
                                tokens[1],
                                None,
                                (time,day,len(players))
                            ))
                    elif tokens[0] == 'KILL':
                        self.events.append(Event(
                            'DECIDE',
                            [(p_id,players[p_id]) for p_id in votes if votes[p_id] == tokens[1]],
                            (tokens[1],tokens[2]),
                            None
                        ))

                    elif tokens[0] == 'NIGHT':
                        votes = {}
                        time = 'NIGHT'
                        day = int(tokens[1])


def readRoles(p_id):
    ''' read a roles file from the path '''
    path = p_id+"/roles"
    if not os.path.exists(path):
        f = open(path,'w')
        f.close()
    f = open(path,'r')
    lines = f.read().split("\n")
    f.close()

    roles = {}
    for line in lines:
        if line == "":
            break
        tokens = line.split()
        roles[tokens[0]] = (int(tokens[1]),int(tokens[2]))

    return roles

def writeRoles(p_id, roles):
    path = p_id + "/roles"

    f = open(path,'w')

    for role,dat in roles.items():
        f.write("{} {} {}\n".format(role,dat[0],dat[1]))

    f.close()

def checkRolesExist(p_id):
    if not os.path.isdir("./"+p_id):
        os.mkdir("./"+p_id)

    if not os.path.exists("./"+p_id+"/roles"):
        f = open("./"+p_id+"/roles", 'w')
        f.close()

def addRole(p_id,role):
    ''' assume we're in the right directory '''
    checkRolesExist(p_id)
    roles = readRoles(p_id)
    if not role in roles:
        roles[role] = (0,0)
    roles[role] = (roles[role][0] + 1, roles[role][1])
    writeRoles(p_id,roles)

def addRoleWin(p_id,role):
    checkRolesExist(p_id)
    roles = readRoles(p_id)
    if not role in roles:
        roles[role] = (0,0)
    roles[role] = (roles[role][0], roles[role][1]+1)
    writeRoles(p_id,roles)

def readPvsOdata(p_id,o_id,name):
    path = p_id+'/'+o_id+"/"+name
    if not os.path.exists(path):
        if not os.path.isdir(p_id+'/'+o_id):
            os.mkdir(p_id+'/'+o_id)
        f = open(path,'w')
        f.close()
    f = open(path,'r')
    lines = f.read().split('\n')
    f.close()

    results = {}
    for line in lines:
        if line == "":
            break
        t = line.split()
        results[(t[0],t[1])] = int(t[2])
    return results

def writePvsOdata(p_id,o_id, name, data):
    path = p_id+"/"+o_id+"/"+name
    f = open(path,'w')
    for (p_role,o_role),num in data.items():
        f.write("{} {} {}\n".format(p_role,o_role,num))
    f.close()

def addPvsOdata(p,o,name):
    p_id = p[0]
    p_role = p[1]
    o_id = o[0]
    o_role = o[1]

    data = readPvsOdata(p_id,o_id,name)
    if not (p_role,o_role) in data:
        data[p_role,o_role] = 0
    data[p_role,o_role] += 1
    writePvsOdata(p_id,o_id,name,data)


def record_event(event):
    ''' Given an event, record in our filesystem
        e_types     active      passive     detail
        START       players     None        (game_num, rules)
        VOTE        voter       votee       ...
        DECIDE      voters      victim      ...
        KILL        (live)mafia victim      ...
        TARGET      actor       target      ...
        WIN         winners     losers      (alive,winning_team)
        REVEAL      revealer    None        (day,time,n_players) '''

    # os.chdir(RECORDS_WORKING_DIRECTORY)

    if event.e_type == 'START':
        for p_id,role in event.active:
            addRole(p_id,role)
    elif event.e_type == 'DECIDE':
        for p in event.active: # voters
            addPvsOdata(p, event.passive, 'votes')
    elif event.e_type == 'KILL':
        for p in event.active:
            addPvsOdata(p, event.passive, 'mtargets')
    elif event.e_type == 'TARGET':
        addPvsOdata(event.active, event.passive, 'targets')
    elif event.e_type == 'TOWN_WIN' or event.e_type == 'MAFIA_WIN':
        for p_id,role in event.active:
            # Winners
            addRoleWin(p_id,role)
    elif event.e_type == 'REVEAL':
        pass

#### Records reading ####
""" We want to have ways to look up statistics. Let's start with some easy ones:
    win ratio | as town | as maf | as role
        For these, have a list. Combine the win ratios for these roles.
    voting accuracy
        When you've voted to kill someone, how likely are they maf? """

def getWinRatio(p_id,counted_roles):
    roles = readRoles(p_id)
    acc = (0,0)

    os.chdir('data/player_records')

    for role in roles:
        if role in counted_roles:
            acc = (acc[0]+roles[role][0], acc[1]+roles[role][1])
    os.chdir('../..')
    return int(100*acc[1]/acc[0])/100

def getNextGame(f):
    line = f.readline().strip()
    lines = [line]
    while (not "WINS" in line) and (not line == ""):
        line = f.readline().strip()
        lines.append(line)
    return lines

###
# if __name__ == "__main__":
#     os.chdir('data')
#     f = open('records','r')
#     lines = getNextGame(f)
#     g = GameRec(lines)
#     os.chdir('player_records')
#     for event in g.events:
#         record_event(event)
#
#     while len(lines) > 2:
#         lines = getNextGame(f)
#         g = GameRec(lines)
#         for event in g.events:
#             record_event(event)
#     f.close()
