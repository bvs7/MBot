# Main info module

# TODO: Reorganize this. Make it much cleaner

import os

DEBUG = 4
SILENT = False

info_fname = "info"

### TIMING ##########

SET_TIMER_VALUE = 5*60

BRIAN_USER_ID = '21642197'

LOBBY_GROUP_ID = '25833774'
DEBUG_GROUP_ID = '40222842'
GROUP_IDS = ['29746651','29746647','29746639',
             '29746635','29746624','29746619']
MODERATORS = ['43040067', '67216752']
ADDRESS = '0.0.0.0'
PORT = '1121'
CALLBACK_URL = 'http://70.171.207.164'
STATS_PORT = '1120'

GROUPY_KEYFILE = "../.groupy.key2"

def log(msg, debug=2):
    if DEBUG >= debug:
        print(msg)

### DATA FOR MSTATE #############

MSTATE_ID_PATH = "data/id"
RECORDS_FILE_PATH = "data/records"
RULES_FILE_PATH = "data/rules"
DET_RECORDS_FILE_PATH = "data/det_records"

RECORDS_WORKING_DIRECTORY = "data/player_records"

MAFIA_ROLES = [ "MAFIA" , "GODFATHER", "STRIPPER"]
TOWN_ROLES    = [ "TOWN", "COP", "DOCTOR", "CELEB", "MILLER", "MILKY"]
ROGUE_ROLES = ["IDIOT"]
ALL_ROLES = TOWN_ROLES + MAFIA_ROLES + ROGUE_ROLES

TEAMS = ["Town", "Mafia", "Rogue"]

# Roles that target at night
TARGET_ROLES = ["DOCTOR","COP","STRIPPER","MILKY"]

GIVE_ROLE = "You are {}" # player role

ROLE_EXPLAIN= {
    "MAFIA" : ("The MAFIA is part of the mafia chat to talk "
               "privately with their co-conspirators. During the day, they try not "
               "to get killed. During the Night, they choose somebody to kill!"),
    "GODFATHER" : ( "The GODFATHER is a leader of the mafia, up "
               "to no good! They use the mafia chat to conspire. If a cop "
               "investigates them, they'll see the GODFATHER as NOT MAFIA!"),
    "TOWN"  : ("The TOWN is a normal player in this game, the last "
               "line of defense against the mafia scum. They sniff out who the "
               "mafia are and convince their fellow town members to kill them "
               "during the day!"),
    "COP"   : ("The COP is the one of the most offensive members of "
               "the townspeople. During the night, they send a direct message to MODERATOR "
               "with the letter of the person they want to investigate, and "
               "upon morning, MODERATOR will tell them whether that person is MAFIA or "
               "NOT MAFIA."),
    "DOCTOR": ("The DOCTOR's job is to save the townspeople from "
               "the mafia scum. During the night, they send a direct message to MODERATOR"
               " with the letter of the person they want to save. If the mafia"
               " targets that person, they will have a near death experience, but "
               "survive."),
    "IDIOT" : ("The IDIOT's dream is to be such an"
               " annoyance that the townsfolk kill them in frustration. They don't"
               " care whether the mafia win or lose, as long as everyone"
               " votes for them."),
    "CELEB" : ("The CELEB is a celebrity. Everybody knows who they are, but everyone "
               "doesn't recognize them right now. CELEB can reveal themselves during Day "
               "by sending MODERATOR '/reveal' and then everyone will know they"
               " are Town. But they ought to be careful! "
               "They'll be quite the target once revealed!"),
    "MILLER" : ("The MILLER is pretty sus but they are actually on the side of Town... "
                "If the cop investigates them, they show up as MAFIA..."),
    "STRIPPER" : ("The STRIPPER is a member of the Mafia with a special ability. "
                  "During the night, they can distract one person. This person can't"
                  " do their job that night (and possibly the following day). "
                  "A distracted COP learns nothing, a distracted DOCTOR can't save,"
                  " and a distracted CELEB can't reveal for a full day!"),
    "MILKY"  : ("The MILKY gives out some milk to someone every night. Other than "
                "that they are a normal townsperson. Don't milk yourself!"),
    }

START_GAME_MESSAGE_MAIN = (
  "Dawn. Of the game and of this new day. You have learned that scum "
  "reside in this town... A scum you must purge. Kill Someone!\nPlayers:\n{}")
       
START_GAME_MESSAGE_MAFIA = "Heyo this is maf chat get it done chaos yeah\nYour Team:\n"

ONLY_VOTE_DAY = "You can only vote during the Day"
SAME_VOTE = "Yes that is your vote, {}"

ONLY_TARGET_NIGHT = "You can only target during the night"
TARGET_SUCCESSFUL = "It is done, targeted {}"

MAFIA_TARGET_PROMPT = "Use /target letter (i.e. /target B) to select someone to kill:"

MILK_SELF_RESPONSE = "Ewwww please don't milk yourself in front of me"

# Rulebook
RULE_BOOK = {
    "known_roles": ("ON", "TEAM", "OFF"),
    "reveal_on_death": ("ON", "TEAM", "OFF"),
    "kick_on_death": ("ON", "OFF"),
    "know_if_saved": ("ON", "DOC", "SELF", "DOC_SELF", "OFF"),
    "start_night": ("ON", "EVEN", "OFF"),
    "standard_roles": ("COP_DOC","OFF"),
    "auto_timer": ("NIGHT", "OFF"),
}


# OP KEYWORDS
ACCESS_KW = '/'

START_KW    = 'start'
IN_KW       = 'in'
OUT_KW      = 'out'
WATCH_KW    = 'watch'
RULE_KW     = 'rule'
RULES_KW    = 'rules'
STATS_KW    = 'stats'

VOTE_KW     = 'vote'
STATUS_KW   = 'status'
HELP_KW     = 'help'
TIMER_KW    = 'timer'
UNTIMER_KW  = 'untimer'
LEAVE_KW    = 'leave'

TARGET_KW   = 'target'
OPTS_KW     = 'options'

REVEAL_KW   = 'reveal'

RESTART_KW  = 'restart'

## HELP MSGS

HELP_MSG = (
    "Welcome, this is MafiaBot. Use this help system to find out more about the game."
    "Try '/help commands' to get a list of possible commands, or /help [ROLE] to learn"
    " about that role. /help [command] will tell you about that command. You can also"
    " direct message MODERATOR with this for privacy.")

LOBBY_HELP_MSG_COMMANDS = (
    "Lobby commands (try '/help start'):\n"
    "/start [minutes] [#people]\n"
    "/status [game]\n"
    "/watch [game]\n"
    "/rule [rule] [setting]\n"
    "/in (DEPRECIATED)\n"
    "/out (DEPRECIATED)\n"
    "/help [subject]\n")

LOBBY_HELP_MSG_START = (
    "/start [minutes] [#people]\n"
    "Creates a Moderator start message. Whoever likes this message within "
    "[minutes] (or 1) minutes will be part of the next game. Game will fail to start"
    " if there are less than [#people] (or 3) players")

LOBBY_HELP_MSG_STATUS = (
    "/status [game]\n"
    "Give the status of current games. Specify a specific game (or a past game)"
    " to see details about that game.")

LOBBY_HELP_MSG_WATCH = (
    "/watch [game]\n"
    "Use this to be added to the main chat of the current game."
    " If there is only one game, [game] isn't needed, otherwise, it specifies "
    "which game to watch."
)

LOBBY_HELP_MSG_RULE = (
    "/rule [rule] [setting]\n"
    "Use this to change the rule setup for future games. Use /rule [rule] to "
    "see the possible settings for a rule and its current setting. /rule [rule]"
    " [setting] will change [rule] to have setting [setting]. Use ''/help "
    "rules' for a list of rules."
)

LOBBY_HELP_MSG_IN = (
    "/in\n"
    "DEPRECIATED. Puts you in the next game. Please just use /start from now on."
)

LOBBY_HELP_MSG_OUT = (
    "/out\n"
    "DEPRECIATED. Takes you out of the next game."
)

MAIN_HELP_MSG_COMMANDS = (
    "Main Chat commands (try '/help vote'):\n"
    "/vote [votee]\n"
    "/status\n"
    "/timer\n"
    "/help [subject]\n"
)

MAIN_HELP_MSG_VOTE = (
    "/vote [votee]\n"
    "Cast your vote for someone\n"
    "'/vote @[name]' casts a vote for [name]\n"
    "'/vote me' votes for yourself\n"
    "'/vote none' retracts your vote\n"
    "'/vote nokill' votes for no kill\n"
    "You need a strong majority (>50%) to kill and a weak majority (>=50%) to no kill"
)

MAIN_HELP_MSG_STATUS = (
    "/status\n"
    "Get the status of the game, namely who is voting for who."
)

MAIN_HELP_MSG_TIMER = (
    "/timer\n"
    "Start a n*5 minute timer where n is the number of living players. "
    "If the timer is already started, reduce its time by 5 minutes. "
    "When the timer runs out, the day or night forcibly progresses."
)

MAIN_HELP_MSG_UNTIMER = (
    "/untimer\n"
    "If you have already /timer'd, then extend the timer by 5 minutes. "
    "If nobody has timer active, the timer is halted and reset."
)

MAFIA_HELP_MSG = (
    "Hey you naughty people/person, use this chat to communicate with other Mafia"
    " or just with me. Try '/options', or '/help commands'"
)

MAFIA_HELP_MSG_COMMANDS = (
    "Mafia Chat Commands (try '/help target'):\n"
    "/target [letter]\n"
    "/options\n"
    "help [subject]"
)

MAFIA_HELP_MSG_TARGET = (
    "/target [letter]\n"
    "During the night, use this to assign your kill to someone. You should get"
    " a confirmation message 'It is done' in response. If you change your mind,"
    " you can re-target in the same way, as long as you do it before morning. "
    "Night ends a random amount of time after all choices have been made."
)

MAFIA_HELP_MSG_OPTIONS = (
    "/options\n"
    "Display the list of options on who to target again. This changes at the "
    "beginning of every night. For example: Brian C. If you want to target Brian,"
    " use '/target C'."
)

DM_HELP_MSG = (
    HELP_MSG +
    "\nIn DM, use /help lobby, /help main, /help mafia for different chat commands"
)

DM_HELP_MSG_COMMANDS = (
    "DM Specific commands:\n"
    "/reveal (If you are CELEB)\n"
    "/target (If you are DOC or COP)\n"
    "/options (If you are DOC or COP)\n"
)

DM_HELP_MSG_START = "In Lobby Chat:\n"+LOBBY_HELP_MSG_START
DM_HELP_MSG_STATUS = "In Lobby Chat:\n"+LOBBY_HELP_MSG_STATUS+"\nIn Main Chat:\n"+MAIN_HELP_MSG_STATUS
DM_HELP_MSG_WATCH = "In Lobby Chat:\n"+LOBBY_HELP_MSG_WATCH
DM_HELP_MSG_RULE = "In Lobby Chat:\n"+LOBBY_HELP_MSG_RULE
DM_HELP_MSG_VOTE = "In Main Chat:\n"+MAIN_HELP_MSG_VOTE
DM_HELP_MSG_TIMER = "In Main Chat:\n"+MAIN_HELP_MSG_TIMER
DM_HELP_MSG_UNTIMER = "In Main Chat:\n"+MAIN_HELP_MSG_UNTIMER
DM_HELP_MSG_TARGET = (
    "In Mafia Chat:\n"+MAFIA_HELP_MSG_TARGET +
    "\nIf you are COP or DOCTOR, use /target [letter] to investigate/save someone here.\n"
    " As COP, upon morning you will learn if that player is MAFIA or NOT MAFIA\n"
    " As DOCTOR, if the mafia tries to save that person, they will live,"
    " try '/help know_if_saved' to learn more about saving rules"
)
DM_HELP_MSG_OPTIONS = MAFIA_HELP_MSG_OPTIONS
DM_HELP_MSG_REVEAL = (
    "If you are a CELEB (try '/help CELEB'), use this to reveal your role. "
    "Moderator will send [your name] is CELEB to the main chat."
)

RULES_HELP_MSG = (
    "List of rules (use /help [rule] for details)"
)
for rule in RULE_BOOK:
    RULES_HELP_MSG += "\n" + rule + " : "
    settings = RULE_BOOK[rule]
    last = len(settings)
    for i in range(last):
        RULES_HELP_MSG += settings[i]
        if not last-1 == i:
            RULES_HELP_MSG += " | "

RULES_HELP_MSG_KNOWN_ROLES = (
    "known_roles : ON | TEAM | OFF\n"
    "ON: A list of roles is given at the beginning of a game.\n"
    "TEAM: The number of players on each team is given at start.\n"
    "OFF: Nothing is given at start."
)

RULES_HELP_MSG_REVEAL_ON_DEATH = (
    "reveal_on_death : ON | TEAM | OFF\n"
    "ON: A player's role (TOWN, COP, MAFIA, etc) is revealed when they die\n"
    "TEAM: A player's team (Maifa, Town) is revealed on death\n"
    "OFF: Don't reveal on death"
)

RULES_HELP_MSG_KICK_ON_DEATH = (
    "kick_on_death : ON | OFF\n"
    "ON: When a player dies they are kicked from the chat\n"
    "OFF: Not that"
)

RULES_HELP_MSG_KNOW_IF_SAVED = (
    "know_if_saved : ON | DOC | SELF | DOC_SELF | OFF\n"
    "ON: When a doctor saves someone that the mafia tried to kill, everybody "
    "learns about it.\n"
    "DOC: A doctor is told if their save is successful.\n"
    "SELF: When a person is successfully saved, they learn about it.\n"
    "DOC_SELF: Both DOC and SELF\n"
    "OFF: Nobody (except mafia I guess) can tell the difference between mafia "
    "not killing and doctor successfully saving"
)

RULES_HELP_MSG_START_NIGHT = (
    "start_night : ON | EVEN | OFF\n"
    "ON: The game begins with Night\n"
    "EVEN: The game begins with Night when an even number of people are playing.\n"
    "OFF: The game begins with Day\n"
)

RULES_HELP_MSG_STANDARD_ROLES = (
    "standard_roles : COP_DOC | OFF\n"
    "COP_DOC: There is at least 1 COP and 1 DOCTOR per game\n"
    "OFF: No guarantees for roles"
)

RULES_HELP_MSG_AUTO_TIMER = (
    "auto_timer : NIGHT | OFF\n"
	"NIGHT: At the beginning of the night, all players' timers are set, resulting in a 5 minute timer\n"
	"OFF: None of that"
)

ROLES_HELP_MSG = (
    "Roles:"
)
for role in (TOWN_ROLES + MAFIA_ROLES + ROGUE_ROLES):
    ROLES_HELP_MSG += role + "\n"

ALL_HELP_MSGS = {
    "rules":    RULES_HELP_MSG,
    "known_roles":      RULES_HELP_MSG_KNOWN_ROLES,
    "reveal_on_death":  RULES_HELP_MSG_REVEAL_ON_DEATH,
    "kick_on_death":    RULES_HELP_MSG_KICK_ON_DEATH,
    "know_if_saved":    RULES_HELP_MSG_KNOW_IF_SAVED,
    "start_night":      RULES_HELP_MSG_START_NIGHT,
    "standard_roles":   RULES_HELP_MSG_STANDARD_ROLES,
    "roles":            ROLES_HELP_MSG,
}

LOBBY_HELP_MSGS={
    "":         HELP_MSG,
    "commands": LOBBY_HELP_MSG_COMMANDS,
    "start":    LOBBY_HELP_MSG_START,
    "status":   LOBBY_HELP_MSG_STATUS,
    "watch":    LOBBY_HELP_MSG_WATCH,
    "rule":     LOBBY_HELP_MSG_RULE,
    "in":       LOBBY_HELP_MSG_IN,
    "out":      LOBBY_HELP_MSG_OUT,
}

MAIN_HELP_MSGS={
    "":         HELP_MSG,
    "commands": MAIN_HELP_MSG_COMMANDS,
    "vote":     MAIN_HELP_MSG_VOTE,
    "status":   MAIN_HELP_MSG_STATUS,
    "timer":    MAIN_HELP_MSG_TIMER,
}

MAFIA_HELP_MSGS={
    "":         MAFIA_HELP_MSG,
    "commands": MAFIA_HELP_MSG_COMMANDS,
    "target":   MAFIA_HELP_MSG_TARGET,
    "options":  MAFIA_HELP_MSG_OPTIONS,
}

DM_HELP_MSGS = {
    "":         DM_HELP_MSG,
    "commands": DM_HELP_MSG_COMMANDS,
    "lobby":    LOBBY_HELP_MSG_COMMANDS,
    "main":     MAIN_HELP_MSG_COMMANDS,
    "mafia":    MAFIA_HELP_MSG_COMMANDS,
    "start":    DM_HELP_MSG_START,
    "status":   DM_HELP_MSG_STATUS,
    "watch":    DM_HELP_MSG_WATCH,
    "rule":     DM_HELP_MSG_RULE,
    "vote":     DM_HELP_MSG_VOTE,
    "timer":    DM_HELP_MSG_TIMER,
    "untimer":  DM_HELP_MSG_UNTIMER,
    "target":   DM_HELP_MSG_TARGET,
    "options":  DM_HELP_MSG_OPTIONS,
    "reveal":   DM_HELP_MSG_REVEAL,
}

# Add universal messages
for role in ROLE_EXPLAIN:
    ALL_HELP_MSGS[role] = ROLE_EXPLAIN[role]

DETERMINED_ROLES = [
    [], #0 (Shouldn't happen)
    ["MAFIA"], #1 (Shouldn't happen)
    ["MAFIA", "DOCTOR"], #2 (Shouldn't happen)
    ["MAFIA","DOCTOR","COP"], #3
    ["MAFIA","DOCTOR","COP","TOWN"], #4
    ["MAFIA","DOCTOR","COP","TOWN","CELEB"], #5
    ["MAFIA","DOCTOR","COP","TOWN","CELEB","GODFATHER"], #6
    ["MAFIA","DOCTOR","COP","TOWN","CELEB","GODFATHER","TOWN"], #7
    ["MAFIA","DOCTOR","COP","TOWN","CELEB","GODFATHER","TOWN","IDIOT"], #8
]
