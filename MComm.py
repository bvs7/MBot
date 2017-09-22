# Python default Group class
#
# This class provides an interface for the program to communicate with a group
#   whether it be GroupMe or any other means to be added.

# An new GroupComm object is created for each group used to communicate with


from MInfo import *

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

    def cast(self, msg):
        """ Send msg to this group """

        print("CAST "+self.title+": "+msg)
        return True

    def ack(self, message_id):
        """ Acknowledge the message given by message_id """
        print("ACK  "+self.title+": "+message_id)
        return True

    def send(self, msg, player_id):
        """ Send a DM to the player with player_id """

        print("SEND "+self.title+", "+player_id+": "+msg)
        return True

    def setTitle(self, new_title):
        """ Rename this group, publicly """
        assert isinstance(new_title, str), "renaming not to a string"

        msg = "TITLE "+self.title+"->"
        self.title = new_title
        msg += self.title

        print(msg)
        return True

    def getName(self,member_id):
        """ Return the name of the member with member_id """
        return "Name of {}".format(member_id)

    def add(self, player_id):
        """ Add player with player_id to this group """
        print("ADD  {}: {}".format(self.title,player_id))
        return True

    def remove(self, player_id):
        """ Remove player with player_id from this group """
        print("RM   {}: {}".format(self.title,player_id))
        return True

    def clear(self, saveList=[]):
        """ Remove all but those in saveList from group """
        print("CLEAR {}".format(self.title))
        return True

    def __str__(self):
        """ Return a string representing this group """

        return "[{}, {}]".format(self.title,self.group_id)


class GroupComm(MComm):

    def __init__(self, group_id):

        self.group_id = group_id

        self.group = self.getGroup(group_id)

        self.title = self.group.name

    def getGroup(self, group_id):
        try:
            groups = [g for g in groupy.Group.list() if g.group_id == group_id]
        except groupy.api.errors.GroupMeError:
            log("FAILED TO GET GROUP")
        if len(groups) >= 1:
            return groups[0]
        else:
            log("Could not find group with id " + group_id)

    def cast(self, msg):
        try:
            groupyEP.Messages.create(self.group_id, msg)
        except groupy.api.errors.GroupMeError:
            log("Failed to Cast")
            return False
        log("CAST "+self.title+": "+msg)
        return True

    def ack(self, message_id):
        try:
            groupyEP.Likes.create(self.group_id, message_id)
        except groupy.api.errors.GroupMeError:
            log("Failed to Ack")
            return False
        log("ACK  "+self.title+": "+message_id)
        return True

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
        self.group.refresh()
        members = self.group.members()
        for m in members:
            if m.user_id == member_id:
                return m.nickname
        log("Failed to get Name")
        return "__"

    def add(self, player_id, player_name):
        self.group.add({'user_id':player_id, 'nickname':player_name})
        log("ADD  {}: {}".format(self.title,player_id))
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
