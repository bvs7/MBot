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
    "MAFIA" : ("You are MAFIA. You are now part of the mafia chat to talk "
               "privately with your co-conspirators. During the day, try not "
               "to get killed. During the Night, choose somebody to kill!"),
    "GODFATHER" : ( "You are a GODFATHER. You are a leader of the mafia, up "
               "to no good! Use the mafia chat to conspire. If a cop "
               "investigates you, they'll see you as TOWN!"),
    "TOWN"  : ("You are TOWN. You are a normal player in this game, the last "
               "line of defense against the mafia scum. Sniff out who the "
               "mafia are and convince your fellow town members to kill them "
               "during the day!"),
    "COP"   : ("You are a COP. You are one of the most powerful members of "
               "the townspeople. During the night, send a direct message to me "
               "with the number of the person you want to investigate, and "
               "upon morning, I will tell you whether that person is town or "
               "mafia."),
    "DOCTOR": ("You are a DOCTOR. Your job is to save the townspeople from "
               "the mafia scum. During the night, send a direct message to me"
               " with the number of the person you want to save. If the mafia"
               " targets them, they will have a near death experience, but "
               "survive."),
    "IDIOT" : ("You are the villiage IDIOT. Your life's dream is to be such an"
               " annoyance that the townsfolk kill you in frustration. You don't"
               " care whether the mafia win or lose, as long as you get votes."),
    "CELEB" : ("You are a CELEBrity. Everybody knows who you are, they just "
               "don't recognize you right now. You can reveal yourself during Day "
               "by sending me '/reveal'. But be careful! You'll be quite the "
               "target once you do this!")
    }

SAVES = [
            "time","day","num_mafia","mafia_target","players","nextPlayerIDs",
            "idiot_winners", "savedRoles", "timer_value", "timerOn", "pref"
        ]

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
    [ 75,     15,       15,    10]
]

# Probability of anti-town roles being chosen
MAFIA_WEIGHTS = [
    ["MAFIA", "IDIOT", "GODFATHER"],
    [ 85,      15,      10],
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

## HELP MESSAGES

LOBBY_HELP_MESSAGE=("Welcome to the Mafia Groupme. This is the Lobby\n"
                    "To join a game, use /in. To start the game, /start\n"
                    "If you change your mind, use /out to leave the next game\n"
                    "To check the status of a current game, use /status\n"
                    "For this help message, try /help\n")

MAIN_HELP_MESSAGE =("Welcome to a Mafia Game! "
                    "In this Groupme you can play mafia via certain commands:\n"
                    "/vote @  - Use this to vote for somebody, where @ is a mention. "
                    "You can also use /vote me to vote yourself, /vote none to cancel "
                    "And /vote nokill to vote for no kill.\n"
                    "/status  - Get the current state of the game\n"
                    "/help  - Display this message\n"
                    "/timer  - Set a five minute time limit on the current day\n")

MAFIA_HELP_MESSAGE = ("Hey you naughty people, here is what you can do here:\n"
                  "/options  - Display the list of what numbers to use to kill.\n"
                  "/target #  - Kill the person who is option #. For example, if "
                  "Brian is option 2, enter '/target 2'\n"
                  "/help  - Display this message.")

DOC_HELP_MESSAGE = ("Hey Doc, here is what you can do here:\n"
                    "/options  - Display the list of what numbers to use to save.\n"
                    "/target #  - Save the person who is option #. For example, if "
                    "Brian is option 2, enter '/target 2'\n"
                    "/help  - Display this message.")

COP_HELP_MESSAGE = ("Hey Cop, here is what you can do here:\n"
                    "/options  - Display the list of what numbers to use to search.\n"
                    "/target #  - Search the person who is option #. For example, if "
                    "Brian is option 2, enter '/target 2'\n"
                    "/help  - Display this message.")

CELEB_HELP_MESSAGE = ("Hey Celeb, here is what you can do here:\n"
                      "/reveal  - MODERATOR will send a message to the main group "
                      " confirming you as town. You can use this whenever you want")

DM_HELP_MESSAGE = ("In the Main Groupme you can play mafia via these commands:\n"
                   "/vote @  - Use this to vote for somebody, where @ is a mention. "
                   "You can also use /vote me to vote yourself, /vote none to cancel "
                   "And /vote nokill to vote for no kill.\n"
                   "/status  - Get the current state of the game. You can also "
                   "enter this command here to privately get the stats\n"
                   "/help  - Display this message\n"
                   "/in  - Be in the NEXT game. During a game, this means the game "
                   "after this one finishes.\n"
                   "/out  - If you change your mind, use this to get out of the "
                   "next game.\n"
                   "/start  - Use this to begin a game with those who have enrolled.\n")

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
