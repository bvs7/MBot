# Python default Group class
#
# This class provides an interface for the program to communicate with a group
#   whether it be GroupMe or any other means to be added.

# A new GroupComm object is created for each group used to communicate with
# Notably, all GroupComm objects have a self.group_id, usable by outside classes

import random
import time

from MInfo import *

groupy_imported = False

try:
    import groupy
    groupy_imported = True
    # Success. Load token
    tokenfile = open("../../.groupy.key")
    token = tokenfile.read()
    tokenfile.close()

    client = groupy.Client.from_token(token)

    # Create static chats
    chats = {}
    for chat in client.chats.list_all():
        chats[chat.other_user['id']] = chat
    
except Exception as e:
    print("Failed to load groupy: {}".format(e))


RETRY_TIMES = 6
RETRY_DELAY = 10
NAME_REPLACE_RATIO = 0.2


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

        self.group = client.groups.get(group_id)
        self.id = group_id
        self.savedNames = {}

    def cast(self, msg):
        for i in range(RETRY_TIMES):
            try:
                m_id = self.group.post(msg).id
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
                    chats[player_id] = groupy.api.chats.Chat(client.chats, other_user=player_id)
                m_id = chats[player_id].post(text=msg).id
                return m_id
            except groupy.exceptions.GroupyError as e:
                print("Failed to send, try {}: {}".format(i,e))
                time.sleep(RETRY_DELAY)

    def setTitle(self, new_title):
        msg = "TITLE "+self.group.name+"->"
        self.group.update(name=new_title)
        msg += self.group.name

        log(msg)
        return True

    # TODO: just process name change mesages
    def getName(self,member_id):
        replace = random.random() < NAME_REPLACE_RATIO
        if member_id in self.savedNames and not replace:
            return self.savedNames[member_id]
        # Update group
        self.group.refresh_from_server()
        self.__refreshNames(member_id)
        if member_id in self.savedNames:
            return self.savedNames[member_id]
        print("Failed to get Name")
        return "__"

    def __refreshNames(self, member_id=None):
        self.group.refresh_from_server()
        if type(member_id) == str:
            member_id = [member_id]
        if not member_id == None:
            for m in self.group.members:
                if m.user_id in member_id:
                    self.savedNames[member_id] = m.nickname

    def add(self, player_id, nickname=None):

        if type(player_id) == str:
            player_id = [player_id]

        for p_id in player_id:
            self.group.memberships.add(nickname, user_id=p_id)
            if nickname != None:
                self.savedNames[p_id] = nickname
            else:
                self.getName(p_id)

    def remove(self, player_id):
        try:
            self.group = client.groups.get(self.group.id)
            memberList = [m for m in self.group.members if m.user_id == player_id]
            for member in memberList:
                if member.user_id != MODERATOR:
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
            if member.user_id != MODERATOR:
                member.remove()
        log("CLEAR {}".format(self.group.name))
        return True

    def __str__(self):
        return "[{}, {}]".format(self.group.name,self.group.id)


class TestMComm(MComm):
    def __init__(self,group_id,silent=False):
        self.group_id = group_id
        self.idToName = {}
        self.silent = silent

    def cast(self, msg):
        if not self.silent:
            print("CAST {}:{}".format(self.group_id,msg)) 

    def ack(self, message_id):
        pass

    def getAcks(self, message_id):
        pass

    def send(self, msg, player_id):
        if not self.silent:
            print("SEND {}:{}".format(player_id,msg))        

    def setTitle(self, new_title):
        pass        

    def getName(self,member_id):
        return member_id

    def add(self, player_id, player_name):
        self.idToName[player_id] = player_name

    def remove(self, player_id):
        _ = self.idToName.pop(player_id, "___")

    def clear(self, saveList=[]):
        self.idToName = {}
        for id in saveList:
            self.idToName[id] = id

    def __str__(self):
        return "Comm({})".format(self.group_id)