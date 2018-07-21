from MComm import TestMComm
from MRecord import TestMRecord
from MState import MState, GameOverException

import traceback

def loadFile(filename):
  with open(filename, 'r') as f:
    pattern = f.readlines()
    pattern = [line.strip() for line in pattern]

  return pattern

TESTS = ["1","2"]
output_log = "results.txt"

mainComm = TestMComm("main")
mafiaComm = TestMComm("mafia")
lobbyComm = TestMComm("lobby")
for i in range(15):
  lobbyComm.add(str(i),str(i))

with open(output_log, 'w') as outf:
  for test in TESTS:
    commands = loadFile(test+".input")
    patterns = loadFile(test+".output")

    rec = TestMRecord(patterns)
    outf.write("Beginning {} test\n".format(test))
    try:
      for command in commands:
        print(command)
        exec(command)
    except AssertionError as ae:
      traceback.print_exc(file=outf)
    except GameOverException as e:
      if rec.pattern:
        outf.write("Extra lines in rec: {}".format(rec.pattern))
      else:
        outf.write("Game ended successfully\n")
    else:
      outf.write("{} successful\n".format(test))
      

