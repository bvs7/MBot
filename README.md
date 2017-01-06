# MBot
---

## Introduction

MBot or Mafia Bot is a simple python server that runs on a raspberry pi. It allows those
in a Groupme chat to play mafia. Groupme Bots listen to chats and DMs for a "MODERATOR"
groupme account. Each new post or direct message (DM) is processed and applied to the game state,
and the MODERATOR account can be used to make posts or DMs in response.

## System Overview

There are 3 group chats used in the game:
  * Lobby Chat
	* Main Chat
	* Mafia Chat

Direct messages (DMs) are also used for certain purposes.

### Lobby Chat

The lobby system is designed to prevent players who aren't in the game from being
spammed too much. From the lobby users can join the next game, watch games, or check
the status of games.

### Main Chat

When the game starts, the players are added to the main chat. From here they can
vote and perform other actions related to the game. This is the chat where the majority
of the game takes place.

### Mafia Chat

## Features to implement


This is Mafia Bot!

Mafia Bot uses the Groupme API to let a group chat play the game Mafia

Currently (11/10/16) the game is structured in the following way:

At least three people must play.
The number of mafia is randomly determined, and relatively fair, based on the number of other players.
The game begins with Day.

Players can enter commands using the command character: '/' followed by a command.

/help		displays a list of commands and uses

Main group commands:

/in		adds the player to the next game
/out		removes them from the next game
/start	begins a game if one is not in progress
/vote		changes the player's vote to the other player they mention
		/vote me, /vote none, /vote nokill also work
/status	lists who is in the next game, or who is in the game and where the votes stand.
/timer	start a five minute timer. At the end of this, the game continues even with no actions

Mafia group (and Cop/Doctor DM) commands:

/target		Sets a player as the target to be killed in the morning
/options	Display the options to target

The game begins when somebody sends the command /start to the main groupme. This assigns roles to everybody currently in the game, and sends out direct messages listing these roles. The Mafia are added to the mafia group chat. Messages are sent announcing the beginning of the game.

Now the game is in the "Day" phase. During this time, everybody votes for somebody to kill. When a vote is determined, the game goes into "Night". During this phase, the mafia, doctor, and cop select who to target. This is resolved as the game returns to day, when the cop is sent a message with info on who they investigated, and the group is informed of a kill/unsuccessful kill.


Features to add:

MASONS		These roles would be for a large mafia group. This is a group chat where everyone is confirmed town.

VIGILANTE		
