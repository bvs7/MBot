# testScript

from MInfo import *
from MController import MController
from MComm import MComm
from ManualServer import TestServer

import time

DEBUG = 1

LIST_OF_TESTS = ["investigate"]

for test in LIST_OF_TESTS:

    lobby = MComm("lobby")

    ctrl = MController(lobby,['1','2'],determined=True)

    t = TestServer(ctrl)

    f = open("tests/"+test + ".input",'r')
    lines = f.read().split('\n')
    f.close()

    for line in lines:
        if DEBUG >= 1:
            print(line)
        if line == "":
            break
        time.sleep(0.001)
        t.run_msg(line)

    rec_f = open(DET_RECORDS_FILE_PATH, 'r')
    out_f = open("tests/"+test + ".output",'r')

    new_out_f = open("tests/"+test+".logout",'w')
    
    rec_f_lines = rec_f.read()
    out_f_lines = out_f.read()

    rec_f.close()
    out_f.close()
    
    new_out_f.write(rec_f_lines)
    new_out_f.close()

    if rec_f_lines == out_f_lines:
        print(test + " passed")
    else:
        print(test + " failed")
        print(rec_f_lines)
        print(out_f_lines)

    del_rec = open(DET_RECORDS_FILE_PATH, 'w')
    del_rec.close()

print("done")
