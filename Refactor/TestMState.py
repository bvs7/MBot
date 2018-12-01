from MComm import TestMComm
from MRecord import TestMRecord
from MState import MState, GameOverException

import traceback

def loadFile(filename):
  with open(filename, 'r') as f:
    pattern = f.readlines()
    pattern = [line.strip() for line in pattern]

  return pattern

TESTS = ["4"]
test_folder = "test_MState/"
output_log = "results.txt"

mainComm = TestMComm("main")
mafiaComm = TestMComm("mafia")
lobbyComm = TestMComm("lobby")
for i in range(15):
  lobbyComm.add(str(i),str(i))

with open(output_log, 'w') as outf:
  for test in TESTS:
    commands = loadFile(test_folder + test+".input")
    patterns = loadFile(test_folder + test+".output")

    rec = TestMRecord(patterns)
    begin_msg = "Beginning {} test\n".format(test)
    outf.write(begin_msg)
    print(begin_msg)
    try:
      command_line = 0
      for command in commands:
        command_line += 1
        if not command == "":
          print(command)
          exec(command)
    except AssertionError as ae:
      traceback.print_exc(file=outf)
      outf.write("command line: {}".format(command_line))
    except GameOverException as e:
      if rec.pattern:
        outf.write("Extra lines in rec: {}".format(rec.pattern))
      else:
        outf.write("Game ended successfully\n")
    else:
      outf.write("{} successful\n".format(test))
      

