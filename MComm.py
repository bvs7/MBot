# Python default Group class
#
# This class provides an interface for the program to communicate with a group
#   whether it be GroupMe or any other means to be added.

# An new GroupComm object is created for each group used to communicate with

import random
from MInfo import *

import time

NAME_REPLACE_RATIO = 0.2

try:
    import groupy

    # Load token
    tokenfile = open("../.groupy.key")
    token = tokenfile.read()
    tokenfile.close()

    client = groupy.Client.from_token(token)

except ImportError:
    log("FAILED TO LOAD GROUPY")


""" MComm Class Description

Variables:
    group_id

Methods:
    cast(msg)
    ack(msg_id)
    getAcks(msg_id)
    send(msg, player_id)
    setTitle(new_title)
    getName(member_id)
    add(player_id)
    remove(player_id)
    clear()
"""

class MComm:

    def __init__(self,group_id):
        """ Initialize group with given group_id """

        # Unique Identifier for this group
        self.group_id = group_id

        self.title = str(group_id)

        self.acks = []

    def cast(self, msg):
        """ Send msg to this group """

        log("CAST "+self.title+": "+msg)
        return True

    def ack(self, message_id):
        """ Acknowledge the message given by message_id """
        log("ACK  "+self.title+": "+str(message_id))
        return True

    def getAcks(self, message_id):
        """ Get the number of acknowledgements for a message """
        return self.acks

    def send(self, msg, player_id):
        """ Send a DM to the player with player_id """

        log("SEND "+self.title+", "+player_id+": "+msg)
        return True

    def setTitle(self, new_title):
        """ Rename this group, publicly """
        assert isinstance(new_title, str), "renaming not to a string"

        msg = "TITLE "+self.title+"->"
        self.title = new_title
        msg += self.title

        log(msg)
        return True

    def getName(self,member_id):
        """ Return the name of the member with member_id """
        return "Name of {}".format(member_id)

    def add(self, player_id):
        """ Add player with player_id to this group """
        log("ADD  {}: {}".format(self.title,player_id))
        return True

    def remove(self, player_id):
        """ Remove player with player_id from this group """
        log("RM   {}: {}".format(self.title,player_id))
        return True

    def clear(self, saveList=[]):
        """ Remove all but those in saveList from group """
        log("CLEAR {}".format(self.title))
        return True

    def __str__(self):
        """ Return a string representing this group """

        return "[{}, {}]".format(self.title,self.group_id)

class GroupComm(MComm):

    def __init__(self, group_id, gen_chats=True):

        self.group = client.groups.get(group_id)
        self.savedNames = {}
        self.hasChats = False
        self.chats = {} # player_id -> chat

        if gen_chats:
            self.chats = self.genChats(client)

    # def getGroup(self, group_id):
    #     try:
    #         groups = [g for g in groupy.Group.list() if g.group_id == group_id]
    #     except groupy.api.errors.GroupMeError:
    #         log("FAILED TO GET GROUP")
    #         return False
    #     if len(groups) >= 1:
    #         return groups[0]
    #     else:
    #         log("Could not find group with id " + group_id)

    def genChats(self, client_):
        chat_list = list(client.chats.list_all())
        for chat in chat_list:
            self.chats[chat.id] = chat
        self.hasChats = True

    def cast(self, msg):
        try:
            message = self.group.post(msg)
        except groupy.exceptions.GroupyError as e:
            log("Failed to Cast: {}".format(e))
            return False
        log("CAST "+self.group.name+": "+msg)
        return message.id

    def ack(self, message_id):
        try:
            self.group.messages.Likes.like(self.group.id, message_id)
        except groupy.exceptions.GroupyError:
            log("Failed to Ack")
            return False
        log("ACK  "+self.group.name+": "+message_id)
        return True

    def getAcks(self, message_id):
        try:
            self.group.update()
        except groupy.exceptions.GroupyError as e:
            log("Failed to get acks: {}".format(e))
            return self.getAcks(message_id)
        msg_id = str(int(message_id)-1) # Subtract 1 so that our message shows up
        for msg in self.group.messages.list_after(msg_id):
            if msg.id == message_id:
                return msg.favorited_by
        return []

    def send(self, msg, player_id):
        if self.hasChats:
            try:
                self.chats[player_id].post(msg)
            except groupy.exceptions.GroupyError as e:
                log("Failed to SEND: {}".format(e))
                return False
            log("SEND "+self.title+", "+player_id+": "+msg)
            return True
        else:
            return False

    def setTitle(self, new_title):
        msg = "TITLE "+self.group.name+"->"
        self.group.update(name=new_title)
        msg += self.group.name

        log(msg)
        return True

    # TODO: just process name change mesages
    def getName(self,member_id):
        if member_id in self.savedNames and random.random() > NAME_REPLACE_RATIO:
            return self.savedNames[member_id]
        try:
            self.group.update()
        except groupy.exceptions.GroupyError as e:
            self.getName(member_id) # TODO: this is dangerous
        members = self.group.members
        for m in members:
            if m.user_id == member_id:
                self.savedNames[member_id] = m.nickname
                return m.nickname
        log("Failed to get Name")
        return "__"

    def add(self, player_id):

        if type(player_id) == list:
            users = []
            for p_id in player_id:
                nickname = None
                if self.hasChats:
                    nickname = self.chats[p_id].other_user.name
                users.append({'nickname':nickname,'user_id':p_id})
            try:
                self.group.memberships.add_multiple(users)
                for user in users:
                    self.savedNames[user['user_id']] = user['nickname']
            except groupy.exceptions.GroupyError as e:
                log("Failed to add: {}".format(e))
                return False
            return True
        else:
            nickname = None
            if self.hasChats:
                nickname = self.chats[player_id].other_user.name
            try:
                self.group.memberships.add(nickname, user_id=player_id)
                self.savedNames[player_id] = nickname
                log("ADD  {}: {}".format(self.group.name,player_id))
            except groupy.exceptions.GroupyError as e:
                print("ERROR ADDING PLAYER:{}".format(e))
                return False
            #self.add(player_id)
            return True

    def remove(self, player_id):
        try:
            self.group.update()
            self.group.memberships.remove(player_id)
        except groupy.exceptions.GroupyError as e:
            log("Failed to remove player: {}".format(e))
            return False
        log("RM   {}: {}".format(self.title,player_id))
        return True

    def clear(self, saveList=[]):
        try:
            self.group.update()
        except groupy.exceptions.GroupyError as e:
            log("Failed to clear group: {}".format(e))
            return False
        for mem_id in saveList:
            self.remove(mem_id)
        log("CLEAR {}".format(self.title))
        return True

    def __str__(self):
        return "[{}, {}]".format(self.title,self.group_id)
