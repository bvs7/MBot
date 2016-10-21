#!/usr/bin/python3

import requests
import groupy
import json

group = [g for g in groupy.Group.list() if g.name == "MAFIA CHAT"]

g = group[0]


try:
  requests.post("http://localhost:1121",json.dumps({'group_id':g.group_id,'text':"/help"}))
except requests.exceptions.ConnectionError as e:
  pass
