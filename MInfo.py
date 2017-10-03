# Main info module

# TODO: CALLBACK_URL in info

import pickle    # For loading vars
import os

DEBUG = 4
SILENT = False

info_fname = "info"

### TIMING ##########

SET_TIMER_VALUE = 5*60



LOBBY_GROUP_ID = '25833774'
GROUP_IDS = ['29746651','29746647','29746639',
             '29746635','29746624','29746619']
MODERATOR = '43040067'
ADDRESS = '0.0.0.0'
PORT = '1121'
CALLBACK_URL = 'http://24.59.62.95'

def log(msg, debug=2):
    if DEBUG >= debug:
        print(msg)

### DATA FOR MSTATE #############

MSTATE_ID_PATH = "data/id"
RECORDS_FILE_PATH = "data/records"
DET_RECORDS_FILE_PATH = "data/det_records"

MAFIA_ROLES = [ "MAFIA" , "GODFATHER"]
TOWN_ROLES    = [ "TOWN", "COP", "DOCTOR", "IDIOT", "CELEB" ]

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
               "with the letter of the person you want to investigate, and "
               "upon morning, MODERATOR will tell them whether that person is MAFIA or "
               "NOT MAFIA."),
    "DOCTOR": ("The DOCTOR's job is to save the townspeople from "
               "the mafia scum. During the night, they send a direct message to MODERATOR"
               " with the letter of the person you want to save. If the mafia"
               " targets that person, they will have a near death experience, but "
               "survive."),
    "IDIOT" : ("The IDIOT's dream is to be such an"
               " annoyance that the townsfolk kill them in frustration. They don't"
               " care whether the mafia win or lose, as long as everyone"
               " votes for them."),
    "CELEB" : ("The CELEB is a celebrity. Everybody knows who they are, but everyone "
               "doesn't recognize you right now. CELEB can reveal themselves during Day "
               "by sending MODERATOR '/reveal'. But they ought to be careful! "
               "They'll be quite the target once revealed!")
    }

# ROLE GENERATION

BASE_SCORE = -8

ROLE_SCORES = {
    "MAFIA"    : -3,
    "GODFATHER" : -3,
    "DOCTOR" :    4,
    "COP"        :    4,
    "TOWN"     :    2,
    "IDIOT"    : -2,
    "CELEB"    :    3,
}

# Probability of town roles being chosen
TOWN_WEIGHTS = [
    ["TOWN", "DOCTOR", "COP", "CELEB"],
    [ 75,     25,       25,    10]
]

# Probability of anti-town roles being chosen
MAFIA_WEIGHTS = [
    ["MAFIA", "IDIOT", "GODFATHER"],
    [ 85,      15,      5],
]


# OP KEYWORDS
ACCESS_KW = '/'

START_KW    = 'start'
IN_KW       = 'in'
OUT_KW      = 'out'
WATCH_KW    = 'watch'
RULE_KW     = 'rule'

VOTE_KW     = 'vote'
STATUS_KW   = 'status'
HELP_KW     = 'help'
TIMER_KW    = 'timer'

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
    "Start a 5 minute timer, at the end of which is nokill. A little broken rn."
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
    HELP_MSG
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
DM_HELP_MSG_TARGET = (
    "In Mafia Chat:\n"+MAFIA_HELP_MSG_TARGET
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
    "List of rules (use /help [rule] for details)\n"
    "known_roles : ON | OFF\n"
    "reveal_on_death : ON | OFF\n"
    "kick_on_death : ON | OFF\n"
    "know_if_saved : ON | OFF"
)

RULES_HELP_MSG_KNOWN_ROLES = (
    "known_roles : ON | OFF\n"
    "ON: A list of roles is given at the beginning of a game.\n"
    "OFF: Not that ¯\\_(ツ)_/¯"
)

RULES_HELP_MSG_REVEAL_ON_DEATH = (
    "reveal_on_death : ON | ONLY_ON_DAY | ONLY_ON_NIGHT | MAF_TOWN | OFF\n"
    "ON: A player's role is revealed when they die\n"
    "ONLY_ON_DAY: (Not implemented) The role is revealed only when a player"
    " is voted out\n"
    "ONLY_ON_NIGHT: (Not implemented) The role is revealed only when killed by "
    "mafia\n"
    "MAF_TOWN: (Not implemented) Only reveal what team the death was on\n"
    "OFF: Don't reveal on death"
)

RULES_HELP_MSG_KICK_ON_DEATH = (
    "kick_on_death : ON | OFF\n"
    "ON: When a player dies they are kicked from the chat\n"
    "OFF: Not that ¯\\_(ツ)_/¯"
)

RULES_HELP_MSG_KNOW_IF_SAVED = (
    "know_if_saved : ON | OFF\n"
    "ON: When a doctor saves someone that the mafia tried to kill, everybody "
    "learns about it.\n"
    "OFF: Nobody (except mafia I guess) can tell the difference between mafia "
    "not killing and doctor successfully saving"
)

ALL_HELP_MSGS = {
    "rules":    RULES_HELP_MSG,
    "known_roles":      RULES_HELP_MSG_KNOWN_ROLES,
    "reveal_on_death":  RULES_HELP_MSG_REVEAL_ON_DEATH,
    "kick_on_death":    RULES_HELP_MSG_KICK_ON_DEATH,
    "know_if_saved":    RULES_HELP_MSG_KNOW_IF_SAVED,

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
