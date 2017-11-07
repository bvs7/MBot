# Python default Group class
#
# This class provides an interface for the program to communicate with a group
#   whether it be GroupMe or any other means to be added.

# An new GroupComm object is created for each group used to communicate with

import random
from MInfo import *

NAME_REPLACE_RATIO = 0.2

try:
    import groupy
    import groupy.api.endpoint as groupyEP
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

    def __init__(self, group_id):

        self.group_id = group_id

        self.group = self.getGroup(group_id)

        self.title = self.group.name

        self.savedNames = {}

    def getGroup(self, group_id):
        try:
            groups = [g for g in groupy.Group.list() if g.group_id == group_id]
        except groupy.api.errors.GroupMeError:
            log("FAILED TO GET GROUP")
            return False
        if len(groups) >= 1:
            return groups[0]
        else:
            log("Could not find group with id " + group_id)

    def cast(self, msg):
        try:
            msg_dict = groupyEP.Messages.create(self.group_id, msg)
        except groupy.api.errors.GroupMeError:
            log("Failed to Cast")
            return False
        log("CAST "+self.title+": "+msg)
        return msg_dict["message"]["id"]

    def ack(self, message_id):
        try:
            groupyEP.Likes.create(self.group_id, message_id)
        except groupy.api.errors.GroupMeError:
            log("Failed to Ack")
            return False
        log("ACK  "+self.title+": "+message_id)
        return True

    def getAcks(self, message_id):
        self.group.refresh()
        msg_id = str(int(message_id)-1) # Subtract 1 so that our message shows up
        for msg in self.group.messages(after=msg_id):
            if msg.id == message_id:
                return msg.likes()
        return []

    def send(self, msg, player_id):
        try:
            groupyEP.DirectMessages.create(player_id, msg)
        except groupy.api.errors.GroupMeError:
            log("Failed to SEND")
            return False
        log("SEND "+self.title+", "+player_id+": "+msg)
        return True

    def setTitle(self, new_title):
        msg = "TITLE "+self.title+"->"

        self.title = new_title
        groupyEP.Groups.update(self.group_id, name=new_title)

        msg += self.title

        log(msg)
        return True

    def getName(self,member_id):
        if member_id in self.savedNames and random.random() > NAME_REPLACE_RATIO:
            return self.savedNames[member_id]
        self.group.refresh()
        members = self.group.members()
        for m in members:
            if m.user_id == member_id:
                self.savedNames[member_id] = m.nickname
                return m.nickname
        log("Failed to get Name")
        return "__"

    def add(self, player_id):
        try:
            self.group.add({'user_id':player_id})
            log("ADD  {}: {}".format(self.title,player_id))
        except Exception as e:
            print("ERROR ADDING PLAYER:{}".format(e))
            self.add(player_id)
        return True

    def remove(self, player_id):
        self.group.refresh()
        for mem in self.group.members():
            if mem.user_id == player_id:
                self.group.remove(mem)
        log("RM   {}: {}".format(self.title,player_id))
        return True

    def clear(self, saveList=[]):
        self.group.refresh()
        for mem in self.group.members():
            if not (mem.user_id in saveList or mem.user_id == MODERATOR):
                self.group.remove(mem)
        log("CLEAR {}".format(self.title))
        return True

    def __str__(self):
        return "[{}, {}]".format(self.title,self.group_id)
