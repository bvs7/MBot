This Mafia Bot is used to play mafia in a groupme.

Currently (10/28/16) the game is structured in the following way:

At least three people must play.
The number of mafia is determinate (no randomness) from the number of players.
There is always one cop and one doctor.
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


Mafia group (and Cop/Doctor DM) commands:

/target	Sets a player as the target to be killed in the morning
/options	Display the options to target

The game begins when somebody sends the command /start to the main groupme. This assigns roles to everybody currently in the game, and sends out direct messages listing these roles. The Mafia are added to the mafia group chat. Messages are sent announcing the beginning of the game.

Now the game is in the "Day" phase. During this time, everybody votes for somebody to kill. When a vote is determined, the game goes into "Night". During this phase, the mafia, doctor, and cop select who to target. This is resolved as the game returns to day, when the cop is sent a message with info on who they investigated, and the group is informed of a kill/unsuccessful kill.


Features to add:

VILLAGE_IDIOT	Role will be added instead of one mafia in games that are biased towards mafia. The village idiot wins if they are killed during the day phase, and loses if they survive until the end or they are killed by the mafia.

Game Generation	Semi-fair games are generated

Time limits		Night will only last so long before nothing happens. Days will have optional limits?

Random Roles	The number of mafia will be randomly generated to be close to a fair level. For example, with 11 players, the amount should be between 3 and 4. This would make the number of mafia a distribution bewteen the two. Other roles could have random assignment elements as well, such as having 2 doctors or the decision to have a village idiot.

CELEBRITY		This role is just a town member that can send /reveal to the moderator to reveal themselves as the celebrity to the main group.

MASONS		These roles would be for a large mafia group. This is a group chat where everyone is confirmed town.

GODFATHER		A mafia variant whom when investigated is shown as TOWN

VIGILANTE		






























