# Python default Group class
#
# This class provides an interface for the program to communicate with a group
#   whether it be GroupMe or any other means to be added.

# An new GroupComm object is created for each group used to communicate with

import random
import time

from MInfo import *

groupy_imported = False

try:
    import groupy
    groupy_imported = True
    # Success. Load token
    tokenfile = open(GROUPY_KEYFILE,'r')
    token = tokenfile.read().strip()
    tokenfile.close()

    client = groupy.Client.from_token(token)

    # Create static chats
    chats = {}
    for chat in client.chats.list_all():
        chats[chat.other_user['id']] = chat

except Exception as e:
    print("Failed to load groupy: {}".format(e))


RETRY_TIMES = 10
RETRY_DELAY = 10
NAME_REPLACE_RATIO = 0.2
ACTION_DELAY = 1


""" A test class that performs the basic functionality for an MComm
    Other MComms are subclasses of this """
class MComm:

    def __init__(self,group_id):
        raise NotImplementedError("MComm init")

    def cast(self, msg):
        raise NotImplementedError("MComm cast")
    def ack(self, message_id):
        raise NotImplementedError("MComm ack")
    def getAcks(self, message_id):
        raise NotImplementedError("MComm getAcks")
    def send(self, msg, player_id):
        raise NotImplementedError("MComm send")
    def setTitle(self, new_title):
        raise NotImplementedError("MComm setTitle")
    def getName(self,member_id):
        raise NotImplementedError("MComm getName")
    def add(self, player_id):
        raise NotImplementedError("MComm add")
    def remove(self, player_id):
        raise NotImplementedError("MComm remove")
    def clear(self, saveList=[]):
        raise NotImplementedError("MComm clear")
    def __str__(self):
        raise NotImplementedError("MComm str")

class GroupComm(MComm):

    def __init__(self, group_id):
        print(group_id)
        self.group = client.groups.get(group_id)
        self.savedNames = {}

    def cast(self, msg):
        for i in range(RETRY_TIMES):
            try:
                m_id = self.group.post(msg).id
                time.sleep(ACTION_DELAY)
                return m_id
            except groupy.exceptions.GroupyError as e:
                print("Failed to cast, try {}: {}".format(i,e))
                time.sleep(RETRY_DELAY)

    def ack(self, message_id):
        try:
            messages = self.group.messages.list_all_after(str(int(message_id)-1))
            for message in messages:
                if message.id == message_id:
                    m = message
                    break
            m.like()
        except groupy.exceptions.GroupyError:
            log("Failed to Ack")
            return False
        log("ACK  "+self.group.name+": "+message_id)
        return True

    def getAcks(self, message_id):
        self.group.refresh_from_server()
        msg_id = str(int(message_id)-1) # Subtract 1 so that our message shows up
        for msg in self.group.messages.list_after(msg_id):
            if msg.id == message_id:
                return msg.favorited_by
        return []

    def send(self, msg, player_id):
        for i in range(RETRY_TIMES):
            try:
                if not player_id in chats:
                    dm = groupy.api.messages.DirectMessages(client.session, player_id)
                    dm.create(HELP_MSG)
                    global chats
                    chats = {}
   #                 time.sleep(1)
                    for chat in client.chats.list_all():
                        print("DM Chat id: " + chat.other_user['id'])
                        chats[chat.other_user['id']] = chat
                if not player_id in chats:
                    raise Exception("Failed to create chat")
                m_id = chats[player_id].post(text=msg).id
                time.sleep(ACTION_DELAY)
                return m_id
            except Exception as e:
                print("Failed to send, try {}: {}".format(i,e))
                time.sleep(RETRY_DELAY)

    def setTitle(self, new_title):
        msg = "TITLE "+self.group.name+"->"
        try:
            self.group.update(name=new_title)
            msg += self.group.name
        except Exception as e:
            print(e)

        log(msg)
        return True

    # TODO: just process name change mesages
    def getName(self,member_id):
        try:
            r = random.random()
            if member_id in self.savedNames and r > NAME_REPLACE_RATIO:
                return self.savedNames[member_id]
            # Update group
            self.group.refresh_from_server()
            for m in self.group.members:
                if m.user_id == member_id:
                    self.savedNames[member_id] = m.nickname
                    return m.nickname
        except Exception as e:
            print("Error getting name: {}".format(e))
        print("Failed to get Name")
        return "__"

    def add(self, player_id, nickname=None):
        for i in range(RETRY_TIMES):
            try:

                if type(player_id) == str:
                    player_id = [player_id]

                if nickname == None:
                    if len(player_id) == 1:
                        nickname = chats[player_id[0]].other_user["name"]
                nickname = None

                users = []
                for p_id in player_id:
                    self.group.memberships.add(nickname, user_id=p_id);
                    if nickname != None:
                        self.savedNames[p_id] = nickname
                    else:
                        self.getName(p_id)
                time.sleep(ACTION_DELAY)
                return
            except groupy.exceptions.GroupyError as e:
                print("Failed to add, try {}: {}".format(i,e))
                time.sleep(RETRY_DELAY)

    def remove(self, player_id):
        try:
            self.group = client.groups.get(self.group.id)
            memberList = [m for m in self.group.members if m.user_id == player_id]
            for member in memberList:
                if not member.user_id in MODERATORS:
                    member.remove()
        except groupy.exceptions.GroupyError as e:
            log("Failed to remove player: {}".format(e))
            return False
        log("RM   {}: {}".format(self.group.name,player_id))
        return True

    def clear(self, saveList=[]):
        try:
            self.group = client.groups.get(self.group.id)
        except groupy.exceptions.GroupyError as e:
            log("Failed to clear group: {}".format(e))
            return False
        for member in self.group.members:
            if not member.user_id in MODERATORS:
                member.remove()
        log("CLEAR {}".format(self.group.name))
        return True

    def __str__(self):
        return "[{}, {}]".format(self.group.name,self.group.id)
