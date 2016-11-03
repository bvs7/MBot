# Main info module

import json  # For loading vars

info_fname = "info"

try:
  f = open(info_fname,'r')
  lines = f.readlines()
  f.close()
except Exception as e:
  print("Error loading info: {}".format(e))

for line in lines:
  words = line.split()
  if len(words) == 2:
    globals()[words[0]] = words[1]
  else:
    print("Couldn't load a line: {}".format(words))

def log(msg, debug=2):
  if DEBUG >= debug:
    print(msg)

class NoteError(Exception):
  def __init__(msg,varName):
    self.msg = msg
    self.varNam = varName

def loadNote(varName):
  """Loads and returns a variable from a file"""
  try:
    return json.load( open(NOTES_FNAME+'/'+varName,'r') )
  except Exception as e:
    log("Falied to load {}: {}".format(varName,e))
    raise NoteError(str(e),varName)

def saveNote(var,name):
  """Saves a variable"""
  try:
    json.dump(var, open(self.NOTES_FNAME+'/'+name,'w'))
  except Exception as e:
    log("Failed to save {}: {}".format(name, e))
    raise NoteError(str(e),name)
