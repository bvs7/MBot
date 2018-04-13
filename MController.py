# Actions that can be taken by the Group

"""
Form of OPS:
LOBBY       (player_id,words,message_id)
MAIN/MAFIA  (mstate,player_id,words,message_id)
DM          (sender_id,words)
"""

import time
import threading
from MInfo import *
from MState import MState, Preferences
from MComm import MComm
import MRecords

class MController:

    def __init__(self,lobbyComm,group_ids,CommType=MComm, determined=False):

        # Current Games
        self.mstates = []

        self.lobbyComm = lobbyComm # MComm lobby

        self.pref = self.load_rules()

        self.availComms = []
        for group_id in group_ids:
            self.availComms.append(CommType(group_id))

        self.determined = determined

        self.time_left = 0
        self.timer_on = False
        self.callback = None
        self.start_message_id = ""
        self.minplayers = 25

        # Ids of players to be added to next game
        self.nextIds = []

        self.init_OPS()

        self.timerThread = threading.Thread(target=self.timer_thread)
        self.timerThread.start()

    def init_OPS(self):
        self.LOBBY_OPS={ HELP_KW   : self.LOBBY_help  ,
                         STATUS_KW : self.LOBBY_status,
                         START_KW  : self.LOBBY_start ,
                         IN_KW     : self.LOBBY_in    ,
                         OUT_KW    : self.LOBBY_out   ,
                         WATCH_KW  : self.LOBBY_watch ,
                         RULE_KW   : self.LOBBY_rule  ,
                         RULES_KW  : self.LOBBY_rule  ,
                         STATS_KW  : self.LOBBY_stats ,
                         }
        # Main OPS
        self.MAIN_OPS ={ VOTE_KW   : self.MAIN_vote  ,
                         STATUS_KW : self.MAIN_status,
                         HELP_KW   : self.MAIN_help  ,
                         LEAVE_KW  : self.MAIN_leave ,
                         TIMER_KW  : self.MAIN_timer ,
                         }

        # Mafia OPS
        self.MAFIA_OPS={ HELP_KW   : self.MAFIA_help   ,
                         TARGET_KW : self.MAFIA_target ,
                         OPTS_KW   : self.MAFIA_options,
                         }

        self.DM_OPS =  { HELP_KW   : self.DM_help  ,
                         STATUS_KW : self.DM_status,
                         OPTS_KW   : self.DM_options,
                         TARGET_KW : self.DM_target  ,
                         REVEAL_KW : self.DM_reveal,
                         STATS_KW  : self.DM_stats,
                         }

    # LOBBY ACTIONS
    # TODO: use a word for more specific help
    def LOBBY_help(self, player_id=None, words=[], message_id=None):
        self.lobbyComm.ack(message_id)
        if len(words) > 1:
            if words[1] in LOBBY_HELP_MSGS:
                self.lobbyComm.cast(LOBBY_HELP_MSGS[words[1]])
                return True
            elif words[1] in ALL_HELP_MSGS:
                self.lobbyComm.cast(ALL_HELP_MSGS[words[1]])
                return True
            else:
                self.lobbyComm.cast("No help for '"+words[1]+"'")
                return True
        else:
            self.lobbyComm.cast(LOBBY_HELP_MSGS[""])
        return True

    # TODO: Select a game for more status

    def LOBBY_status(self, player_id=None,words=[], message_id=None):
        self.lobbyComm.ack(message_id)

        msg = self.__get_status()
        self.lobbyComm.cast(msg)
        return True

    def __get_status(self):
        if len(self.mstates) == 0:
            msg = "No Games"
        elif len(self.mstates) == 1:
            msg = str(self.mstates[0])
        elif len(self.mstates) > 1:
            msg = "Current Games\n"
            for m in self.mstates:
                msg += "{}: {} {}; {} Players\n".format(
                    m.id, m.time, m.day, len(m.players) )
        if self.timer_on:
            m = self.time_left//60
            msg += "\nNew Game starting within {} minute{}".format(m,'s' if m == 1 else '')
        return msg

    # TODO: have LOBBY like the /in to acknowledge
    def LOBBY_in(self, player_id,words=[], message_id=None):
        self.lobbyComm.ack(message_id)

        # Add to next list
        if player_id not in self.nextIds:
            self.nextIds.append(player_id)
            msg = "{} added to next game:".format(self.lobbyComm.getName(player_id))
        else:
            msg = "You are already in the next game"
        for p_id in self.nextIds:
            msg += "\n" + self.lobbyComm.getName(p_id)
        self.lobbyComm.cast(msg)
        return True

    def LOBBY_out(self, player_id,words=[], message_id=None):
        self.lobbyComm.ack(message_id)

        # try to remove from list:
        if player_id in self.nextIds:
            self.nextIds.remove(player_id)
            self.lobbyComm.cast(
                "{} removed from next game".format(self.lobbyComm.getName(player_id)))
        else:
            self.lobbyComm.cast(
                "{} wasn't in the next game".format(self.lobbyComm.getName(player_id)))
        return True


    def LOBBY_start(self, player_id=None, words=[], message_id=None):
        self.lobbyComm.ack(message_id)

        minutes = 1
        minplayers = 3
        if len(words) > 2:
            try:
                minutes = int(words[1])
                minplayers = int(words[2])
                if minutes < 1:
                    minutes = 1
            except ValueError:
                pass
        elif len(words) > 1:
            try:
                minutes = int(words[1])
                if minutes < 1:
                    minutes = 1
            except ValueError:
                pass

        self.minplayers = minplayers
        msg = ("Game will start in {} minute{} ({}). (If there are at least {} players)"
               " Like this to join.").format(minutes, '' if minutes==1 else 's',
                                             time.strftime("%I:%M",time.localtime(time.time()+(minutes*60))),
                                             minplayers)
        self.start_message_id = self.lobbyComm.cast(msg)
        self.start_timer(minutes, self.start_game)
        return True

    def start_game(self):

        toAdd = self.lobbyComm.getAcks(self.start_message_id)

        for member_id in toAdd:
            if not member_id in self.nextIds:
                self.nextIds.append(member_id)

        if len(self.nextIds) >= 3 and len(self.nextIds) >= self.minplayers:
            if len(self.availComms) >= 2:
                self.lobbyComm.cast("Starting Game")
                mainComm = self.availComms.pop()
                mafiaComm = self.availComms.pop()
                mstate = MState(self.nextIds,mainComm,mafiaComm,self.lobbyComm,
                                preferences=self.pref,
                                final=self.mstate_final, determined = self.determined)
                self.mstates.append(mstate)
                self.nextIds.clear()
            else:
                self.lobbyComm.cast("Too many games")
        else:
            self.lobbyComm.cast("Not enough players to start a game")
            self.nextIds.clear()
        return True

    def mstate_final(self,mstate):
        self.availComms.append(mstate.mainComm)
        self.availComms.append(mstate.mafiaComm)
        self.lobbyComm.cast(mstate.roleString)
        self.mstates.remove(mstate)

    def LOBBY_watch(self, player_id,words=[], message_id=None):
        self.lobbyComm.ack(message_id)

        if len(self.mstates) == 0:
            self.lobbyComm.cast("No game to watch")
            return True
        if len(self.mstates) == 1:
            return self.mstates[0].mainComm.add(player_id, self.lobbyComm.getName(player_id))

        if words[1].isnumeric() and int(words[1]) < len(self.mstates):
            return self.mstates[int(words[1])].mainComm.add(player_id, self.lobbyComm.getName(player_id))
        else:
            msg = "Watch which game? (use /watch [#]):\n"
            for m in self.mstates:
                msg += "{}: {} {}; {} players\n".format(
                    m.game_num, m.time, m.day, len(m.players) )
            self.lobbyComm.cast(msg)
            return True

    def LOBBY_rule(self, player_id=None,words=[], message_id=None):

        self.lobbyComm.ack(message_id)

        if len(words)<3: # Not enough to specify rule
            msg = "To change a rule, use /rule [rule] [setting]"
            for rule in self.pref.book:
                msg += "\n{}: {}".format(rule,self.pref.book[rule])
            self.lobbyComm.cast(msg)
            return True

        if words[1] in RULE_BOOK:
            if words[2] in RULE_BOOK[words[1]]:
                self.pref.book[words[1]] = words[2]
                self.save_rules()
                self.lobbyComm.cast("Changed {} to {}".format(words[1],words[2]))
                return True
            else:
                self.lobbyComm.cast("\"{}\" not a valid setting for {}".format(words[2],words[1]))
                return False
        else:
            self.lobbyComm.cast("\"{}\" not a valid rule, use '/help rules' for help".format(words[1]))
            return False

    def save_rules(self):
        f = open(RULES_FILE_PATH, 'w')
        for rule in self.pref.book:
            f.write(rule+"|"+self.pref.book[rule]+"\n")
        f.close()
        return True

    def load_rules(self):
        pref = Preferences()
        f = open(RULES_FILE_PATH, 'r')
        line = f.readline()
        while '\n' in line:
            words = line.strip().split("|")
            pref.book[words[0]] = words[1]
            line = f.readline()
        f.close()
        return pref

    def LOBBY_stats(self, player_id, words, message_id):
        self.lobbyComm.ack(message_id)

        if len(words) > 1:
            if words[1] == "winrate" or words[1] == "record":
                counted_roles = TOWN_ROLES + MAFIA_ROLES
                if len(words) > 2 and words[2] == "Town":
                    counted_roles = TOWN_ROLES
                if len(words) > 2 and words[2] == "Mafia":
                    counted_roles = MAFIA_ROLES
                if len(words) > 2 and words[2] in TOWN_ROLES + MAFIA_ROLES + ROGUE_ROLES:
                    counted_roles = words[2]
                (won,tot) = MRecords.getWinRatio(player_id,counted_roles)
                if words[1] == "winrate":
                    if tot == 0:
                        tot = 1
                    msg = "{} Win Rate: {}%".format(self.lobbyComm.getName(player_id),int(won/tot*100))
                elif words[1] == "record":
                    msg = "{} Record: {} Games, {} Won, {} Lost".format(self.lobbyComm.getName(player_id),tot,won,tot-won)
                self.lobbyComm.cast(msg)

        return True


    # MAIN ACTIONS

    def MAIN_help(self,mstate, player_id=None,words=[], message_id=None):
        mstate.mainComm.ack(message_id)
        if len(words) > 1:
            if words[1] in MAIN_HELP_MSGS:
                mstate.mainComm.cast(MAIN_HELP_MSGS[words[1]])
                return True
            elif words[1] in ALL_HELP_MSGS:
                mstate.mainComm.cast(ALL_HELP_MSGS[words[1]])
                return True
            else:
                mstate.mainComm.cast("No help for '"+words[1]+"'")
                return True
        else:
            mstate.mainComm.cast(MAIN_HELP_MSGS[""])
        return True

    def MAIN_status(self,mstate,player_id=None,words=[], message_id=None):
        mstate.mainComm.ack(message_id)

        mstate.mainComm.cast(str(mstate))
        return True

    def MAIN_vote(self,mstate,player_ids,words=[], message_id=None):
        # where player_ids is a tuple of voter, votee
        mstate.mainComm.ack(message_id)

        voter = player_ids[0]
        votee = player_ids[1]

        return mstate.vote(voter,votee)

    def MAIN_leave(self, mstate, player_id, words=[], message_id=None):
        mstate.mainComm.ack(message_id)

        if player_id in [player.id for player in mstate.players]:
            mstate.mainComm.cast("You can't leave, aren't you playing?")
        else:
            mstate.mainComm.remove(player_id)
        return True

    def MAIN_timer(self,mstate,player_id=None,words=[], message_id=None):
        mstate.mainComm.ack(message_id)
        result = False
        for player in mstate.players:
            if player.id == player_id:
                result = mstate.setTimer()
        return result

    # MAFIA ACTIONS
    def MAFIA_help(self,mstate,player_id=None,words=[], message_id=None):
        mstate.mafiaComm.ack(message_id)
        if len(words) > 1:
            if words[1] in MAFIA_HELP_MSGS:
                mstate.mafiaComm.cast(MAFIA_HELP_MSGS[words[1]])
                return True
            elif words[1] in ALL_HELP_MSGS:
                mstate.mafiaComm.cast(ALL_HELP_MSGS[words[1]])
                return True
            else:
                mstate.mafiaComm.cast("No help for '"+words[1]+"'")
                return True
        else:
            mstate.mafiaComm.cast(MAFIA_HELP_MSGS[""])
        return True

    def MAFIA_target(self,mstate,player_id=None,words=[], message_id=None):
        mstate.mafiaComm.ack(message_id)

        for player in mstate.players:
            if player.id == player_id and player.role in MAFIA_ROLES:

                try:
                    return mstate.mafiaTarget(words[1][0])
                except Exception as e:
                    log("Invalid Mafia Target {}".format(e))
        return False

    def MAFIA_options(self,mstate,player_id=None,words=[], message_id=None):
        mstate.mafiaComm.ack(message_id)

        return mstate.mafia_options()

    # DM ACTIONS

    def __DM_get_mstate(self,words,sender_id):
        sender_mstates = []
        for mstate in self.mstates:
            if sender_id in [p.id for p in mstate.players]:
                sender_mstates.append(mstate)

        m = None

        if len(sender_mstates) == 0:
            #self.lobbyComm.sendDM(LOBBY_HELP_MESSAGE,sender_id)
            return None
        elif len(sender_mstates) == 1:
            m = sender_mstates[0]
        elif len(sender_mstates) > 1:
            if words[1].isnumeric():
                for mstate in sender_mstates:
                    if mstate.id == int(words[1]):
                        m = mstate
            if m == None:
                return None
        return m

    def DM_help(self,sender_id,words):
        if len(words) > 1:
            if words[1] in DM_HELP_MSGS:
                self.lobbyComm.send(DM_HELP_MSGS[words[1]], sender_id)
                return True
            elif words[1] in ALL_HELP_MSGS:
                self.lobbyComm.send(ALL_HELP_MSGS[words[1]], sender_id)
                return True
            else:
                self.lobbyComm.send("No help for '"+words[1]+"'", sender_id)
                return True
        else:
            self.lobbyComm.send(DM_HELP_MSGS[""], sender_id)
        return True

    def DM_status(self,sender_id,words):
        m = self.__DM_get_mstate(words,sender_id)

        if m == None:
            self.lobbyComm.send(self.__get_status(),sender_id)
            return True

        m.mainComm.send(str(m),sender_id)
        return True

    def DM_target(self,sender_id,words):
        m = self.__DM_get_mstate(words,sender_id)

        if m == None:
            return True

        player = m.getPlayer(sender_id)
        if not player.role in TARGET_ROLES:
            return True

        if len(words) >= 2 and words[1].isalpha():
            return m.target(sender_id,words[1][0])
        if len(words) >= 3 and words[2].isalpha():
            return m.target(sender_id,words[2][0])

        return self.DM_options(words,sender_id)

    def DM_options(self,sender_id,words):
        m = self.__DM_get_mstate(words,sender_id)

        if m == None:
            return True

        player = m.getPlayer(sender_id)
        if not player.role in TARGET_ROLES:
            return True
        prompt = ""
        if player.role == "DOCTOR":
            prompt = "Use /target letter (i.e. /target D) to pick someone to save"
        elif player.role == "COP":
            prompt = "Use /target letter (i.e. /target A) to pick someone to investigate"
        elif player.role == "STRIPPER":
            prompt = "Use /target letter (i.e. /target C) to pick someone to distract"
        m.send_options(prompt,sender_id)
        return True

    def DM_stats(self,sender_id,words):
        if len(words) > 1:
            if words[1] == "winrate" or words[1] == "record":
                counted_roles = TOWN_ROLES + MAFIA_ROLES
                if len(words) > 2 and words[2] == "Town":
                    counted_roles = TOWN_ROLES
                if len(words) > 2 and words[2] == "Mafia":
                    counted_roles = MAFIA_ROLES
                if len(words) > 2 and words[2] in TOWN_ROLES + MAFIA_ROLES + ROGUE_ROLES:
                    counted_roles = words[2]
                (won,tot) = MRecords.getWinRatio(sender_id,counted_roles)
                if words[1] == "winrate":
                    if tot == 0:
                        tot = 1
                    msg = "{} Win Rate: {}%".format(self.lobbyComm.getName(sender_id),int(won/tot*100))
                elif words[1] == "record":
                    msg = "{} Record: {} Games, {} Won, {} Lost".format(self.lobbyComm.getName(sender_id),tot,won,tot-won)
                self.lobbyComm.send(msg, sender_id)
        return True

    def DM_reveal(self,sender_id,words):
        m = self.__DM_get_mstate(words,sender_id)

        if m == None:
            return True

        player = m.getPlayer(sender_id)
        return m.try_reveal(sender_id)


    def start_timer(self, minutes, callback):
        self.time_left = minutes * 60
        self.timer_on = True
        self.callback = callback

    def timer_thread(self):
        while True:
            time.sleep(1)
            if self.timer_on:
                self.time_left -= 1
                if self.time_left <= 0:
                    self.callback()
                    self.timer_on = False
