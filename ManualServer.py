# Test Server

from MInfo import *
from MController import MController
from MComm import MComm

class PlayerIDWrapper:
    def __init__(self, id_):
        self.user_id = id_

    def __str__(self):
        return "(" + str(self.user_id) + ")"

class TestServer:

    def __init__(self, controller):

        self.ctrl = controller

    def run(self):
        """ An input needs a sender_id, content, and a group

        Default group is Lobby, format is:
        sender_id [mstate_id] : content
        3 required words
        """

        msg_id = 0

        while True:

            msg = input('->')

            msg_id += 1

            if msg == 'quit':
                break

            self.run_msg(msg,msg_id)

    def run_msg(self, msg, msg_id=0):

        raw_words = msg.split()

        if len(raw_words) < 3:
            print("sender_id [mstate_id] : content")
            return

        sender_id = raw_words[0]

        if sender_id == "DM":
            sender_id = raw_words[1]
            words = raw_words[3:]

            if words[0] in self.ctrl.DM_OPS:
                self.ctrl.DM_OPS[words[0]](sender_id,words)
                return

        mstate_id = 0 # Lobby id

        if raw_words[1] == ':':
            words = raw_words[2:]
        elif raw_words[2] == ':':
            mstate_id = raw_words[1]
            words = raw_words [3:]
        else:
            log("Format:\nsender_id [mstate_id] : content")
            return

        ## Begin server stuff

        if len(words) < 1:
            return

        if words[0] == START_KW:
            for user_id in words[1:]:
                self.ctrl.lobbyComm.acks.append(PlayerIDWrapper(user_id))
            self.ctrl.minplayers = 3
            self.ctrl.start_game()
            return

        if words[0] == VOTE_KW:
            if len(words) >= 2:
                sender_id = (sender_id, words[1])

        mafia = False
        mstate = None
        if not mstate_id == 0:
            if 'm' in mstate_id:
                mafia = True
                mstate_id = mstate_id.replace('m','')
            for m in self.ctrl.mstates:
                if mstate_id == str(m.game_num):
                    mstate = m
                    break

        if mstate_id == 0 and words[0] in self.ctrl.LOBBY_OPS:
            self.ctrl.LOBBY_OPS[words[0]](sender_id,words,msg_id)
        elif mafia and words[0] in self.ctrl.MAFIA_OPS and not mstate == None:
            self.ctrl.MAFIA_OPS[words[0]](mstate,sender_id,words,msg_id)
        elif words[0] in self.ctrl.MAIN_OPS and not mstate == None:
            self.ctrl.MAIN_OPS[words[0]](mstate,sender_id,words,msg_id)


if __name__ == "__main__":

    lobby = MComm("lobby")

    ctrl = MController(lobby,['1','2'],determined=True)

    t = TestServer(ctrl)

    f = open(DET_RECORDS_FILE_PATH, 'w')
    f.close()
