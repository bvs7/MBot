# TestMain

from MInfo import *
from MController import MController
from MComm import MComm
from ManualServer import TestServer

def checkGame(obs_rec_path, des_recs):
    f = open(obs_rec_path, 'r')

    line = f.readline().strip()

    index = 0

    while not line == des_recs[index]:
        line = f.readline().strip()
        if line == "":
            f.close()
            return "MISSED FIRST LINE"
    
    while not line == "":
        if not line == des_recs[index]:
            print(line + "|" + des_recs[index])
            f.close()
            return index
        line = f.readline().strip()
        index += 1

    f.close()

    if index == len(des_recs):
        return "PASSED"
    else:
        return "FAILED"

def test(msgs, recs):

    lobby = MComm("lobby")

    ctrl = MController(lobby,['1','2','3','4','5','6'], determined = True)

    server = TestServer(ctrl)

    f = open("data/det_records", 'w')
    f.close()

    for msg in msgs:
        server.run_msg(msg, 0)

    print( checkGame("data/det_records",recs))

if __name__ == "__main__":

    msgs = [
        "1 : in",
        "2 : in",
        "3 : in",
        "1 : start",
        "1 1 : vote 1",
        "2 1 : vote 1"
        ]

    recs = [
        "Game Begins",
        "Name of 1 votes for Name of 1",
        "Name of 2 votes for Name of 1",
        "Name of 1 (MAFIA) is killed (2-0)",
        "TOWN WINS"
        ]
    #test(msgs, recs)

    lobby = MComm("lobby")

    ctrl = MController(lobby,['1','2','3','4','5','6'], determined = True)

    server = TestServer(ctrl)

    f = open("data/det_records", 'w')
    f.close()

    server.run()

    
    

    
