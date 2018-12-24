from MComm import TestMComm
from MRecord import TestMRecord
from DBMRecord import DBMRecord
from MState import MState, GameOverException

import traceback

def loadFile(filename):
  with open(filename, 'r') as f:
    pattern = f.readlines()
    pattern = [line.strip() for line in pattern]

  return pattern

TESTS = ["4"]
test_folder = "test_MState/"

mainComm = TestMComm("main")
mafiaComm = TestMComm("mafia")
lobbyComm = TestMComm("lobby")
for i in range(15):
  lobbyComm.add(str(i),str(i))

for test in TESTS:
  commands = loadFile(test_folder + test+".input")
  rec = DBMRecord("TestMRecords")
  begin_msg = "Beginning {} test\n".format(test)
  print(begin_msg)
  try:
    command_line = 0
    for command in commands:
      command_line += 1
      if not command == "":
        print(command)
        exec(command)
  except AssertionError as ae:
    pass
  except GameOverException as e:
    pass
