# Represents A game of Mafia

from MInfo import *
from MComm import MComm

import random
import threading
import time

# TODO: create an exception for the game ending

class Player:
    """
    Vote is normally another player. If it is None, there is no vote yet,
    if it is self.__null, it is a vote for nokill.
    Target is similar.
    """
    def __init__(self,id,role="",vote=None,target=None):
        self.id = id
        self.role = role
        self.vote = vote
        self.target = target

    def __str__(self):
        return "[{}, {}]".format(self.id,self.role)

class Preferences:
    """
    Holds all of the preference variables for how the game is played
    """
    def __init__(self,
                 known_roles="ON",
                 reveal_on_death="ON",
                 kick_on_death="ON",
                 know_if_saved="ON",
                 start_night="OFF",
                 standard_roles="OFF"):
        self.book = {}
        # Show the roles at the beginning of the game
        # known_roles ON | TEAM | OFF
        #   ON: All roles are known at the start
        #   TEAM: Amount of Mafia and Town is known
        #   OFF: No roles are known
        self.book["known_roles"] = known_roles
        # Show a player's role on their death
        # reveal_on_death ON | TEAM | OFF
        #   ON: Show role on death
        #   TEAM: Show MAFIA or TOWN on death
        #   OFF: Don't show role on death
        self.book["reveal_on_death"] = reveal_on_death
        # Kick a player from the game when they die
        self.book["kick_on_death"] = kick_on_death
        # If the doctor successfully saves, everyone knows who was saved
        self.book["know_if_saved"] = know_if_saved

        self.book["start_night"] = start_night

        self.book["standard_roles"] = standard_roles

    def __str__(self):

        result = ""
        for rule,setting in self.book.items():
            result += rule + ": " + setting + "\n"
        result = result[0:-1]
        return result

"""
MState Class Description

p means player_id OR player object

Methods:
    MState(playerIDs, mainComm, mafiaComm, lobbyComm,...)
    vote(voter_id, votee_id)
    mafiaTarget(target_option)
    mafiaOptions()
    target(p,target_option)
    sendOptions(prompt,p)
    reveal(p)
    startGame(nextPlayerIDs, pref)
    getPlayer(p)
    setTimer()
"""

class MState:
    """Holds the state of a Mafia game. When it is created, two chats are created with it
    And it creates a GroupyComm to communicate with those chats"""

    id = 0 # Assign IDs starting from 0+1
    # TODO: Fix saves etc
    def __init__(self, playerIDs, mainComm, mafiaComm, lobbyComm,
                 preferences=None, final=None, determined = False):
        log("MState init",3)

        self.record = ""

        # This mstate is determined and won't have any randomness
        self.determined = determined

        if self.determined:
            self.game_num = 1
        else:
            try:
                f = open(MSTATE_ID_PATH,'r')
                next_id = f.readline()
                self.game_num = int(next_id)

                f.close()

                f = open(MSTATE_ID_PATH,'w')
                f.write(str(self.game_num + 1))
                f.close()
            except FileNotFoundError as e:
                self.game_num = -1
                log(e)

        self.__record("Creating Game #"+str(self.game_num))

        self.mainComm = mainComm
        self.mafiaComm = mafiaComm
        self.lobbyComm = lobbyComm

        # The GroupComm objects used to respond to stimuli
        self.mainComm.setTitle("MAIN CHAT #"+str(self.game_num))
        self.mafiaComm.setTitle("MAFIA CHAT #"+str(self.game_num))

        # Preferences for the current game
        if preferences == None:
            self.pref = Preferences() #TODO: default pref setting
        else:
            self.pref = Preferences()
            for rule in preferences.book:
                self.pref.book[rule] = preferences.book[rule]

        self.__record(str(self.pref))

        # fn run on completion
        self.final = final

        # Generic player object used for recording the number voting for no kill
        self.null = Player("0","null")

        # "Day"/"Night" and number representing current day. 0 is no game
        self.time = "Day"
        self.day = 0

        self.num_mafia = 0    # number of remaining mafia
        self.players = []    # A list of PLAYER objects currently in the game

        # A list of the roles people were assigned at the beginning of the game.
        # Used to reveal roles at the end
        self.savedRoles = {}

        self.mafia_target = None    # A player object that the mafia has targeted

        self.idiot_winners = []    # A list of players who won by being an idiot that was voted out


        self.timer_value = 0    # The amount of time left when timer is on
        self.timerOn = False    # if Timer is on

        self.roleString = ""    # Listing of roles

        self.getNameMemory = {}


        # Start this game
        self.startGame(playerIDs,preferences=self.pref)

        # Begin a thread that will keep track of the timer
        self.timerThread = threading.Thread(name="Timer"+str(self.game_num), target=self.__watchTimer)
        self.timerThread.start()

    def vote(self,voter_id,votee_id):
        """ Makes voter change vote to votee, then checks for lynch. """
        log("MState vote",3)
        if not self.time == "Day":
            log("{} couldn't vote for {}: Not Day".format(voter_id,votee_id))
            self.mainComm.cast("Can't vote at Night")
            return True
        try:
            voter = self.getPlayer(voter_id)
            if votee_id == None:
                votee = None
            elif votee_id == "0":
                votee = self.null
            else:
                votee = self.getPlayer(votee_id)
        except Exception as e:
            log(e)
            return False
        voter.vote = votee
        self.__record(self.mainComm.getName(voter_id) + " votes for " +
                      self.mainComm.getName(votee_id))
        self.__checkVotes(votee)
        return True

    def mafiaTarget(self,target_option):
        """ Change Mafia's target to players[target_option] """
        log("MState mafiaTarget",3)
        if not self.time == "Night":
            log("Mafia couldn't target {}: Not Night".format(target_option))
            return False
        try:
            target_number = ord(target_option.upper())-ord('A')
            if target_number == len(self.players):
                target = self.null
            elif target_number == None:
                target = None
            else:
                target = self.players[target_number]
        except Exception as e:
            log("Mafia failed to target {}: {}".format(target_option, e))
            return False
        self.mafia_target = target
        self.mafiaComm.cast("It is done")

        self.__record("Mafia targets " + self.mainComm.getName(target.id))

        # Check if Night is over
        self.__checkToDay()
        return True

    def mafia_options(self):
        """ Send the mafia's options to the mafia chat. """
        log("MState mafia_options",3)
        msg = "Use /target letter (i.e. /target B) to select someone to kill:"
        c = 'A'
        for player in self.players:
            msg += "\n"+c+" "+self.mainComm.getName(player.id)
            c = chr(ord(c)+1)
        msg += "\n"+c+" No kill"
        self.mafiaComm.cast(msg)
        return True

    def target(self,p,target_option):
        """ Change p's target to players[target_option]. """
        log("MState target",3)
        if not self.time == "Night":
            log("{} couldn't target {}: Not Night".format(p,target_option))
            return False

        # Check if the player is represented as an object or a string
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Couldn't find target from {}: {}".format(p,e))
            return False
        try:
            target_number = ord(target_option.upper())-ord('A')
            if target_number == len(self.players):
                target = self.null
            elif target_number == None:
                target = None
            else:
                target = self.players[target_number]
            player.target = target
        except Exception as e:
            log("{} failed to target {}: {}".format(player.id, target_option, e))
            return False

        self.mainComm.send("It is done",player.id)
        self.__record("{} ({}) targets {}".format(self.mainComm.getName(player.id),
                                                  player.role,
                                                  self.mainComm.getName(target.id)))
        # Check if Night is over
        self.__checkToDay()
        return True

    def send_options(self,prompt,p):
        """ Send list of options to player p with preface prompt. """
        log("MState send_options",3)
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Couldn't send options to {}: {}".format(p,e))
        msg = prompt
        c = 'A'
        for p in self.players:
            msg += "\n"+c+" "+self.mainComm.getName(p.id)
            c = chr(ord(c)+1)
        msg += "\n"+c+" No target"
        return self.mainComm.send(msg,player.id)

    def reveal(self,p):
        """ Reveal a player's role to the Main Chat """
        log("MState reveal",3)
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Could not reveal {}: {}".format(p,e))
            return False
        self.mainComm.cast(self.mainComm.getName(player.id) + " is " + player.role)
        self.__record(self.mainComm.getName(player.id) + " is revealed as " + player.role)
        return True

    def revealTeam(self,p):
        """ Reveal a player's team to the Main Chat """
        log("MState revealTeam",3)
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Could not reveal team {}: {}".format(p,e))
            return False
        if player.role in MAFIA_ROLES:
            team = "Mafia"
        elif player.role in TOWN_ROLES:
            team = "Town"
        self.mainComm.cast(self.mainComm.getName(player.id) + " is on team " + team)
        self.__record(self.mainComm.getName(player.id) + " is revealed on team " + team)
        return True

    def startGame(self, nextPlayerIDs, preferences=None):
        """ Gen roles, create player objects and start the game. """
        log("MState startGame",3)

        # Set preference variables
        if not preferences == None:
            self.pref = preferences

        num_players = len(nextPlayerIDs)
        if num_players < 3:
            return False

        # Initialize game variables
        self.day = 1
        self.time = "Day"

        self.mafiaComm.clear()
        self.mainComm.clear()
        self.players.clear()
        self.savedRoles.clear()
        self.num_mafia = 0

        if not self.determined:
            random.shuffle(nextPlayerIDs)

        if not self.determined:
            roles = self.__genRoles(num_players)
        else:
            roles = DETERMINED_ROLES[num_players]

        for i in range(len(nextPlayerIDs)):
            player = Player(nextPlayerIDs[i], roles[i])
            self.players.append(player)
            log("Adding player: {},{}".format(player.id,self.mainComm.getName(player.id)))
            self.savedRoles[player.id] = player.role

            if player.role in MAFIA_ROLES:
                self.num_mafia += 1

        random.shuffle(self.players)

        for player in self.players:
            self.mainComm.add(player.id)
            self.mainComm.send("You are {}\n".format(player.role)+ ROLE_EXPLAIN[player.role],player.id)
            if player.role in MAFIA_ROLES:
                self.mafiaComm.add(player.id)

        # Get roleString for later
        self.roleString = self.__revealRoles()

        self.__record(self.roleString)

        score = BASE_SCORE
        for role in roles:
            score += ROLE_SCORES[role]

        msg = ("Dawn. Of the game and of this new day. You have learned that scum "
                     "reside in this town... A scum you must purge. Kill Someone!")

        msg += "\nDifficulty Score: " + str(score)

        msg += "\nPlayers:"
        for p in self.players:
            msg += "\n " + self.mainComm.getName(p.id)
        if self.pref.book["known_roles"] == "ON":
            msg += "\nThe Roles:" + self.__showRoles(roles)
        elif self.pref.book["known_roles"] == "TEAM":
            msg += "\nThe Teams:" + self.__showTeams(roles)

        self.mainComm.cast(msg)

        msg = "Heyo this is maf chat get it done chaos yeah\nYour friends are:"
        for p in self.players:
            if p.role in MAFIA_ROLES:
                msg += "\n" + self.mafiaComm.getName(p.id)
        self.mafiaComm.cast(msg)

        if (self.pref.book["start_night"] == "ON" or
           (self.pref.book["start_night"] == "EVEN" and len(self.players)%2 == 0)):
            self.__toNight()

        self.__record("Game Begins")

        return True

    def getPlayer(self, p):
        """ p can be player or id, either way returns the player object associated. """
        log("MState getPlayer",5)
        if type(p) == Player:
            return p
        elif type(p) == str:
            players = [player for player in self.players if player.id == p]
            if len(players) >= 1:
                return players[0]
            else:
                raise Exception("Couldn't find player from id {}".format(p))
        else:
            raise Exception("Couldn't find player from {}".format(p))

    def setTimer(self):
        """ Start a 5 minute timer. At the end of which the game will automatically progress. """
        log("MState setTimer",3)
        if not (self.timerOn or self.day == 0):
            self.timerOn = True
            self.timer_value = SET_TIMER_VALUE
            self.mainComm.cast("Timer Started. Five minutes left")
            return True
        else:
            return False


    #### HELPER FN ####

    def __kill(self, p):
        """ Remove player p from the game. """
        log("MState __kill",4)

        rec = self.mainComm.getName(p.id) + " (" + p.role + ")" + " is killed "
        # Check if the player is represented as an object or a string
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Couldn't kill {}: {}".format(p,e))
            return False

        # Remove player from game
        try:
            if player.role in MAFIA_ROLES:
                self.num_mafia = self.num_mafia - 1
            self.players.remove(player)
        except Exception as e:
            log("Failed to kill {}: {}".format(player,e))
            return False

        self.__record(rec + "(" + str(len(self.players) - self.num_mafia) +
                            "-" + str(self.num_mafia) + ")")
        # Check win conditions
        if not self.__checkWinCond():
            # Game continues, let the person know roles
            self.mainComm.send(self.roleString,player.id)
            # Depending on preferences, kick, or reveal
            if self.pref.book["reveal_on_death"] == "ON":
                self.reveal(player)
            elif self.pref.book["reveal_on_death"] == "TEAM":
                self.revealTeam(player)
            if self.pref.book["kick_on_death"] == "ON":
                self.mainComm.remove(player.id)
                self.mafiaComm.remove(player.id)

        return True

    def __checkVotes(self,p):
        """ See if there is a majority of votes for p, if so, kill p and go toNight."""
        log("MState __checkVotes",4)
        if p == None:
            self.mainComm.cast("Vote Retraction successful")
            return True
        try:
            player = self.getPlayer(p)
        except Exception as e:
            log("Could not check votes for {}: {}".format(p,e))
        num_voters = len([v for v in self.players if v.vote == player])
        num_players = len(self.players)
        if player == self.null:
            if num_voters >= num_players/2:
                self.mainComm.cast("You have decided not to kill anyone")
                self.__record("Nobody is killed")
                self.__toNight()
                return True
            else:
                self.mainComm.cast("Vote successful: {} more vote{}to decide not to kill".format(
                                    int((num_players+1)/2) - num_voters,
                                    " " if (int((num_players+1)/2) - num_voters == 1) else "s "))
                return True
        if num_voters > num_players/2:
            self.mainComm.cast("The vote to kill {} has passed".format(
                                self.mainComm.getName(player.id)))
            if(self.__kill(player)):
                if player.role == "IDIOT":
                    self.idiot_winners.append(player)
                if not self.day == 0:
                    self.__toNight()
        else:
            self.mainComm.cast("Vote successful: {} more vote{}until {} is killed".format(
                     int((num_players)/2+1)-num_voters,
                     " " if int((num_players)/2+1)-num_voters == 1 else "s ",
                     self.mainComm.getName(player.id) ))
            return True

    def __checkToDay(self):
        """ Check if all night roles are done, if so, call toDay. """
        log("MState __checkToDay",4)
        cop_doc_done = True
        for p in self.players:
            if p.role in ["COP","DOCTOR"] and p.target == None:
                cop_doc_done = False

        if (self.mafia_target == None or not cop_doc_done):
            return False
        else:
            self.__toDay()
            return True

    def __toDay(self):
        """ Change state to day, realizing the mafia's target and all other targets. """
        log("MState __toDay",4)

        self.__record("Day " + str(self.day) + " begins")

        self.time = "Day"
        self.day = self.day + 1
        self.mainComm.cast("Uncertainty dawns, as does this day")
        # If mafia has a target
        if not self.mafia_target in [None, self.null]:
            # Doctor is alive and saved the target
            target_saved = False
            for p in self.players:
                if (p.role == "DOCTOR" and not p.target == None and
                        p.target.id == self.mafia_target.id):
                    target_saved = True
                    if "DOC" in self.pref.book["know_if_saved"]:
                        self.mainComm.send("Your save was successful!",p.id)
                    if "SELF" in self.pref.book["know_if_saved"]:
                        self.mainComm.send("You were saved!", p.target.id)
            if target_saved:
                if self.pref.book["know_if_saved"] == "ON":
                    msg = ("Tragedy has struck! {} is ... wait! They've been saved by "
                           "the doctor! Someone must pay for this! Vote to kill "
                           "somebody!").format(self.mainComm.getName(self.mafia_target.id))
                else:
                    msg = ("A peculiar feeling drifts about... everyone is still alive...")
                self.mainComm.cast(msg)
                self.__record(self.mainComm.getName(self.mafia_target.id) +" was saved")
            # Doctor couldn't save the target
            else:
                if self.day == 0:
                    return True
                try:
                    msg = ("Tragedy has struck! {} is dead! Someone must pay for this! "
                             "Vote to kill somebody!").format(self.mainComm.getName(self.mafia_target.id))
                    self.mainComm.cast(msg)
                    self.__kill(self.mafia_target)
                except Exception:
                    pass
        # Mafia has no target
        else:
            msg = ("A peculiar feeling drifts about... everyone is still alive...")
            self.mainComm.cast(msg)

        # If cop is still alive and has chosen a target
        for p in self.players:
            if p.role == "COP" and (not p.target in [None, self.null]):
                msg = "{} is {}".format(
                    self.mainComm.getName(p.target.id),
                    "MAFIA" if (p.target.role in MAFIA_ROLES and
                    not p.target.role == "GODFATHER") else "NOT MAFIA")
                self.mainComm.send(msg,p.id)
                self.__record(self.mainComm.getName(p.id) +" investigates " +
                              self.mainComm.getName(p.target.id) + " (" +
                              p.target.role + ")")

        self.__clearTargets()
        self.timerOn = False
        return True

    def __toNight(self):
        """ Change state to Night, send out relevant info. """

        self.__record("Night " + str(self.day) + " begins")

        self.timerOn = False

        self.time = "Night"
        for p in self.players:
            p.vote = None
        self.mainComm.cast("Night falls and everyone sleeps")
        self.mafiaComm.cast("As the sky darkens, so too do your intentions. "
                            "Pick someone to kill")
        self.mafia_options()
        for p in self.players:
            if p.role == "COP":
                self.send_options("Use /target letter (i.e. /target C) "
                                  "to pick someone to investigate",p.id)
            elif p.role == "DOCTOR":
                self.send_options("Use /target letter (i.e. /target D) "
                                  "to pick someone to save",p.id)
        #self.setTimer()
        return True

    def __clearTargets(self):
        """ Clear all player's targets. """
        log("MState __clearTargets",4)
        for p in self.players:
            p.target = None
        self.mafia_target = None

    def __checkWinCond(self):
        """ Check if a team has won, if so end the game. """
        log("MState __checkWinCond",4)
        # Check win conditions
        if self.num_mafia == 0:
            self.mainComm.cast("TOWN WINS")
            self.__record("TOWN WINS")
            self.__endGame("TOWN")
            return True
        elif self.num_mafia >= len(self.players)/2:
            self.mainComm.cast("MAFIA WINS")
            self.__record("MAFIA WINS")
            self.__endGame("MAFIA")
            return True
        return False

    def __endGame(self, winners):
        """ Reset State and end the game. """
        log("MState __endGame",4)
        self.day = 0
        self.time = "Day"
        self.timerOn = False
        self.players.clear()

        for winner in self.idiot_winners:
            self.mainComm.cast(self.maiComm.getName(winner.id)+" WON!")
        self.idiot_winners.clear()

        rfp = DET_RECORDS_FILE_PATH if self.determined else RECORDS_FILE_PATH
        self.__recordGame(rfp,winners)

        self.final(self)
        return True

    def __record(self, msg):
        self.record += msg + "\n"

    def __recordGame(self,rec_path,winners):
        f = open(rec_path, 'a')
        f.write(self.record)
        f.close()


    # TODO: Get this string at the start of the game
    def __revealRoles(self):
        """ Make a string of the original roles that the game started with. """
        log("MState __revealRoles",4)
        r = "GG, here were the roles:"
        for player_id,role in self.savedRoles.items():
            r += "\n" + self.mainComm.getName(player_id) + ": " + role
        return r

    def __showRoles(self,roles):
        """ Make a string which describes the number of players with each role. """
        log("MState __showRoles",4)

        roleDict = {}
        for role in roles:
            if role in roleDict:
                roleDict[role] += 1
            else:
                roleDict[role] = 1
        msg = ""
        for role in roleDict:
                msg += "\n" + role + ": " + str(roleDict[role])
        return msg

    def __showTeams(self,roles):
        """ Make a string which describes the number of players on each team. """
        log("MState __showTeams",4)

        teamDict = {"Mafia":0, "Town":0}
        for role in roles:
            if role in MAFIA_ROLES:
                teamDict["Mafia"] += 1
            elif role in TOWN_ROLES:
                teamDict["Town"] += 1
            elif role == "IDIOT":
                if not "Unaligned" in teamDict:
                    teamDict["Unaligned"] = 0
                teamDict["Unaligned"] += 1

        msg = ""
        for key in teamDict:
            msg += "\n" + key + ": " + str(teamDict[key])
        return msg


    def __addUntil(self, role, weights):
        """ Helper for genRoles """
        log("MState __addUntil",5)
        result = 0
        for i in range(len(weights[0])):
            result += weights[1][i]
            if weights[0][i] == role:
                break
        return result

    def __genRoles(self, num_players):
        """ Create a list of roles of length num_players. Uses random but semi-fair assignment """
        log("MState __genRoles",4)
        assert(num_players >= 3)
        while(True):
            n = 0
            score = BASE_SCORE
            roles = []
            num_mafia = 0
            num_town = 0
            num_idiot = 0
            town_sum = sum(TOWN_WEIGHTS[1])
            mafia_sum = sum(MAFIA_WEIGHTS[1])
            role = "TOWN"

            # if self.pref.book["standard_roles"] == "COP_DOC":
            #     roles = ["COP","DOCTOR"]
            #     num_town = 2
            #     n = 2
            #     score += ROLE_SCORES["COP"] + ROLE_SCORES["DOCTOR"]

            if num_players == 4:
                return ["TOWN", "DOCTOR", "COP", "MAFIA"]
            elif num_players == 3:
                return ["DOCTOR", "MAFIA", "COP"]
            while(n < num_players):
                if score < 0:
                    # Add Town
                    t = random.randint(0,town_sum)
                    for i in range(len(TOWN_WEIGHTS[0])):
                        if t < sum(TOWN_WEIGHTS[1][0:(i+1)]):
                            role = TOWN_WEIGHTS[0][i]
                            break
                    num_town += 1
                else:
                    # Add Mafia
                    m = random.randint(0,mafia_sum)
                    for i in range(len(MAFIA_WEIGHTS[0])):
                        if m < sum(MAFIA_WEIGHTS[1][0:(i+1)]):
                            role = MAFIA_WEIGHTS[0][i]
                            break
                    if not role == "IDIOT":
                        num_mafia += 1
                    else:
                        num_idiot += 1
                roles.append(role)
                score += ROLE_SCORES[role]
                if role == "GODFATHER":
                    score -= len([None for c in roles if c == "COP"])
                if role == "COP":
                    score -= len([None for g in roles if g == "GODFATHER"])
                n += 1

            if self.pref.book["standard_roles"] == "COP_DOC":
                if len(c for c in roles if c == "COP") < 1 or len(d for d in roles if d == "DOCTOR") < 1:
                    continue # Try generating again. Until we have a game with COP and DOC...    

            # Done making roles, ensure this isn't a bad game
            if not ((num_mafia + num_idiot + 2 >= num_town) or (num_mafia == 0)):
                break

        # Roles contains a valid game
        return roles

    def __watchTimer(self):
        """ Ticks a timer and switches to the next stage when we take too long. """
        log("MState __watchTimer",5)
        lastTime = self.time
        lastDay    = self.day
        while True:
            log("MState __watchTimer TICK",6)
            try:
                currTime = self.time
                currDay    = self.day
                if self.timerOn:
                    if((not currDay == 0) and currTime == lastTime and currDay == lastDay):
                        self.timer_value -= 1
                if self.timerOn:
                    if self.timer_value == 60:
                        self.mainComm.cast("One minute remaining, one minute")
                    elif self.timer_value == 20:
                        self.mainComm.cast("Twenty Seconds")
                    elif self.timer_value == 0:
                        if currTime == "Day":
                            self.mainComm.cast("You are out of time")
                            self.__toNight()
                            self.timerOn = False
                            self.timer_value = 0
                        elif currTime == "Night":
                            self.mainComm.cast("Some people slept through the night")
                            self.__toDay()
                            self.timerOn = False
                            self.timer_value = 0

                lastTime = currTime
                lastDay    = currDay

                #Wait For a second
                time.sleep(1)
            except Exception as e:
                log("Error with __watchTimer: {}".format(e))

    def __saveState(self):
        """ Return a string that can be written to a file to uniquely represent
            this game """
        log("MState __saveState",5)

    def __str__(self):
        """ Return the status of the game. """
        log("MState __str__",5)
        if self.day == 0:
            m = "Ready to start a new game.\n"
            for p in self.nextPlayerIDs:
                m += "{}\n".format(self.mainComm.getName(p))
        else:
            m = "GAME #{}: {} {}: ".format(self.game_num,self.time,self.day)
            if self.timerOn:
                m += time.strftime("%M:%S",time.gmtime(self.timer_value))
            m += "\n"
            for player in self.players:
                m += self.mainComm.getName(player.id) + " : "
                count = 0
                for voter in [v for v in self.players if v.vote == player]:
                    count += 1
                    m += self.mainComm.getName(voter.id) + ", "
                m += str(count) + "\n"

        if self.pref.book["known_roles"] == "ON" and self.pref.book["reveal_on_death"] == "ON":
            m += self.__showRoles([p.role for p in self.players])
        elif self.pref.book["known_roles"] in ("ON","TEAM") and self.pref.book["reveal_on_death"] in ("ON","TEAM"):
            m += self.__showTeams([p.role for p in self.players])
        else:
            roles = []
            for r in self.savedRoles.values():
                roles.append(r)
            if self.pref.book["known_roles"] == "ON":
                m += "\nOriginal Roles:" + self.__showRoles([self.savedRoles.values()])
            elif self.pref.book["known_roles"] == "TEAM":
                m += "\nOriginal Teams:" + self.__showTeams([self.savedRoles.values()])

        return m
