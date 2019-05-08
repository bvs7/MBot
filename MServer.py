#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import threading
import time
import json

from MInfo import *
from MComm import MComm, GroupComm
from MState import MState
from MController import MController
from DBMRecord import DBMRecord


class MServer:

  def __init__(self, MCommType=MComm, #default MComm type
               MStateType=MState, # default MState type
               restart=True):
    self.MCommType = MCommType
    self.MStateType = MStateType

    self.ctrl = MController(LOBBY_GROUP_ID, GROUP_IDS)

  def do_POST(self,post):

    if 'text' in post:
      text = post['text']
    else:
      return
    
    if len(text) >= len(ACCESS_KW) and text[0:len(ACCESS_KW)] == ACCESS_KW:
      keyword = text.split()[0][1:]
    else:
      return

    group_id = None
    message_id = None
    sender_id = None

    if 'group_id' in post:
      group_id = post['group_id']
    if 'id' in post:
      message_id = post['id']
    if 'sender_id' in post:
      sender_id = post['sender_id']

    self.ctrl.command(keyword, group_id, message_id, sender_id, post)

if __name__ == "__main__":
  mserver = MServer(GroupComm)

class MainHandler(BaseHandler):

  def do_POST(self):
    try:
      length = int(self.headers['Content-Length'])
      content = self.rfile.read(length).decode('utf-8')
      post = json.loads(content)
    except Exception as e:
      post = {}
      log("failed to load content")


    mserver.do_POST(post)
    return

if __name__ == "__main__":
  server = HTTPServer((ADDRESS,int(PORT)), MainHandler)

  serverThread = threading.Thread(name="Server Thread", target=server.serve_forever)

  serverThread.start()

  while True:
    pass
