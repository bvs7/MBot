# MBot

## Introduction

MBot or Mafia Bot is a simple python server that runs on a raspberry pi. It allows those
in a Groupme chat to play mafia. Groupme Bots listen to chats and DMs for a "MODERATOR"
groupme account. Each new post or direct message (DM) is processed and applied to the game state,
and the MODERATOR account can be used to make posts or DMs in response.

## System Overview

There are 3 group chats used in the game:
* **Lobby Chat** - The lobby system is designed to prevent players who aren't in the game from being
spammed too much. From the lobby users can join the next game, watch games, or check
the status of games.
* **Main Chat** - When the game starts, the players are added to the main chat. From here they can
vote and perform other actions related to the game. This is the chat where the majority
of the game takes place.
* **Mafia Chat** - The players chosen to be mafia are all added to this chat so that they can communicate,
know who each other are, and can all perform mafia actions.

Direct messages (DMs) are also used for certain purposes.
DMs are most important for players who are cops, doctors, etc. They use DMs to choose
who to save/investigate or perform other role actions. Any player can use simple commands
over DM if they need help.

## System Design

### Files
There are 4 python files used for the game:
* **GroupyComm.py** - A class file used for output. Easy way to get user's names, cast messages to groups
and send DMs to players.
* **MState.py** - A class file used to represent and modify the current game.
* **MInfo.py** - This file initializes global variables and functions.
* **MServer.py** - This is the main file. It sets up GroupyComm and MState instances, creates a server
that listens for bots' POST requests, and processes those requests into the correct actions on MState.

There is also an info file that contains key id numbers as well as a notes folder, which is used to save
MState state.

### Commands

In each of the chats, there are commands that can be entered prefixed by a '/' character.

#### Lobby Commands

* `/in` - The id of the user who enters this command is added to a list of players who will
participate in the next game.
* `/out` - This user is removed from the list for the next game.
* `/start` - The game is started with those in the list for the next game.
* `/status` - Responds with the status of the game occuring, or a message that no game is occuring.
* `/help` - Responds with a description of commands for Lobby Chat.

#### Main Commands

* `/vote` - Used to vote for someone to die
  * `/vote @[mention]` - If another player is mentioned, they are voted for.
  * `/vote me` - The player votes for themself.
  * `/vote nokill` - The player votes for nobody to be killed this day.
  * `/vote none` - The player retracts their vote.
* `/timer` - Starts a five minute timer during the day. Once this timer runs out,
no kill will take place and the game advances to night.
* `/status` - Responds with the status of the game, including time, day, members remaining,
and who is voting for whom.
* `/help` - Responds with a list of commands that can be used in Main Chat.

#### Maifa Commands

* `/target [#]` - Selects the person who was assigned the given number as Mafia's target for the night.
* `/options` - Lists the players to kill and their numbers for this night.
* `/help` - Responds with a list of commands that can be used in Mafia Chat.

#### DM Commands

* `/status` - Gives the current status of the game.
* `/help` - Responds with a help message specific to the player's role.
* `/target [#]` - Used by cop and doctor to target a player to investigate/save.
* `/reveal` - Used by the celeb to reveal their innocence to the group.

## Game Overview

The game begins when somebody sends the command /start to the main groupme. This assigns roles to everybody currently in the game, and sends out direct messages listing these roles. The Mafia are added to the mafia group chat. Messages are sent announcing the beginning of the game.

Now the game is in the "Day" phase. During this time, everybody votes for somebody to kill. When a vote is determined, the game goes into "Night". During this phase, the mafia, doctor, and cop select who to target. This is resolved as the game returns to day, when the cop is sent a message with info on who they investigated, and the group is informed of a kill/unsuccessful kill.

## TODO

- [x] Known Roles - Make an option for the roles (but not the players who have them) to be shared at the beginning of the game.
- [x] Reveal on Death - Make an option for a person's role to be revealed when they die.
- [ ] Nickname Updates - Make nicknames stored in MState update when someone changes their nickname
- [ ] Records - The results of each game are saved to help adjust for fairness and find problems.
  - [ ] Auto Records - Update the record system after each game finishes
  - [ ] Record Types - Decide what should be kept track of during games and how to keep track of it
  - [ ] Record Viewer - Design and Create an intuitive way to view records that avoids spam
- [x] Better Timer - Make a timer that is flexible and less disastrous than a five minute permanent timer.
  - [x] Untimer - Implement the untimer command so that a timer can be stopped
  - [ ] Timers status - Add the status of who has started a timer to status
  - [ ] Auto night timer option - Create a new rule that can make timer on at night by default
- [ ] MILKY - Create a new role that gives milk to someone each night (possibly a role modifier?)
  - [ ] Implement permenant statistics (like milk)
- [ ] Make new options for IDIOT kills
  - [ ] Game ends when IDIOT is killed :(
  - [ ] IDIOT gets to revenge kill someone who voted for them when they are killed
  - [ ] IDIOT gets to revenge kill a non-MAFIA aligned player that voted for them
- [ ] GUARD - Create a new Rogue role whos goal is to help someone else survive to the end of the game.
