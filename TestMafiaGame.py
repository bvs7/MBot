#!/usr/bin/python3

import requests
import groupy
import json

mainGroup = [g for g in groupy.Group.list() if g.group_id == "25833774"][0]
mafiaGroup= [g for g in groupy.Group.list() if g.group_id == "25941870"][0]

mem = mainGroup.members()

def getMem(name):
  result = [m for m in mem if m.nickname == name]
  if len(result) >= 1:
    return result[0]


def post(message, member=getMem("Brian"),group=mainGroup, mentions=None):

  x = {
    'group_id':group.group_id,
    'user_id':member.user_id,
    'text':message,
    }

  if mentions == None:
    x['attachments'] = []
  else:
    x['attachments'] = [{'type':'mentions','user_ids':[mentions]}]
  
  try:
    requests.post("http://localhost:1121", json.dumps(x))
  except Exception as e:
    print(e)
