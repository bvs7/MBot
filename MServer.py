#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler as BaseHandler,HTTPServer

import threading
import time
import json

from MInfo import *
from MComm import MComm, GroupComm
from MState import MState
from MController import MController


class MServer:

    def __init__(self, MCommType=MComm, #default MComm type
                     MStateType=MState, # default MState type
                     restart=True):
        log("MServer init",3)
        self.MCommType = MCommType
        self.MStateType = MStateType

        self.ctrl = MController(self.MCommType(LOBBY_GROUP_ID), GROUP_IDS)

    def do_POST(self,post):
        """Process a POST request from bots watching the chats"""
        log("MServer do_POST",3)

        # Check that this is a command
        if post['text'][0:len(ACCESS_KW)] == ACCESS_KW:

            # Check if this was posted by the DM bot
            if '+' in post['group_id']:
                return self.do_DM(post)

            try:
                words = post['text'][len(ACCESS_KW):].split()
                player_id = post['user_id']
                message_id = post['id']
                group_id = post['group_id']
            except KeyError as e:
                log("KeyError:" + str(e))
                return

            if group_id == self.ctrl.lobbyComm.group_id:
                if words[0] in self.ctrl.LOBBY_OPS:
                    return self.ctrl.LOBBY_OPS[words[0]](player_id,words,message_id)
            for mstate in self.ctrl.mstates:
                if group_id == mstate.mainComm.group_id:
                    if words[0] in self.ctrl.MAIN_OPS:

                        # CHECK FOR A VOTE
                        if words[0] == VOTE_KW:
                            if len(words) < 2: # shouldn't happen?
                                votee = None
                            else:
                                if words[1].lower() == "me":
                                    votee = player_id
                                elif words[1].lower() == "none":
                                    votee = None
                                elif words[1].lower() == "nokill":
                                    votee = "0"
                                elif 'attachments' in post:
                                    mentions = [a for a in post['attachments'] if a['type'] == 'mentions']
                                    if len(mentions) > 0 and 'user_ids' in mentions[0] and len(mentions[0]['user_ids']) >= 1:
                                        votee = mentions[0]['user_ids'][0]
                            player_id = (player_id, votee)

                        return self.ctrl.MAIN_OPS[words[0]](mstate,player_id,words,message_id)
                elif gorup_id == mstate.mafiaComm.group_id:
                    if words[0] in self.ctrl.MAFIA_OPS:
                        return self.ctrl.MAFIA_OPS[words[0]](mstate,player_id,words,message_id)

    def do_DM(self,DM):
        """Process a DM from a player"""
        log("MServer do_DM",3)
        assert 'sender_id' in DM, "No sender_id in DM for do_DM"
        assert 'text' in DM, "No text in DM for do_DM"
        # Check that this is a valid command
        if (not DM['sender_id'] == MODERATOR and DM['text'][0:len(ACCESS_KW)] == ACCESS_KW):
            words = DM['text'][len(ACCESS_KW):].split()

            sender_id = DM['sender_id']

            if len(words) > 1:
                return self.ctrl.DM_OPS[words[0]](sender_id,words)

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

  #  try:
    print(post)
    mserver.do_POST(post)
#    except Exception as e:
 #       log(e)
    return

if __name__ == "__main__":

    server = HTTPServer((ADDRESS,int(PORT)), MainHandler)

    serverThread = threading.Thread(name="Server Thread", target=server.serve_forever)

    serverThread.start()

    while True:
        pass
