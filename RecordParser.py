#!/usr/bin/python3

import sys

class Game_Record:

    def __init__(self, f):
        line = f.readline()
        while (not line == "") and (not "GG" in line):
            line = f.readline()
        if line == "":
            self.state = "N" # No game
            return

        self.role_dict = {"TOWN":0,"MAFIA":0,"COP":0,"DOCTOR":0,"GODFATHER":0,
                          "IDIOT":0,"CELEB":0}
        self.town_num = 0
        self.maf_num = 0
        self.idiot_num = 0
        self.state = "R" #Getting roles
        while self.state == "R":
            line = f.readline()
            for role in ("TOWN", "MAFIA", "COP", "DOCTOR", "GODFATHER", "IDIOT", "CELEB"):
                if role in line:
                    self.role_dict[role] += 1
                    if role in ("TOWN","COP","DOCTOR","CELEB"):
                        self.town_num += 1
                    elif role in ("MAFIA","GODFATHER"):
                        self.maf_num += 1
                    elif role == "IDIOT":
                        self.idiot_num += 1
                    break
            if "Game Begins" in line:
                self.state = "W" # look for winner

        while self.state == "W":
            line = f.readline()
            if "MAFIA WINS" in line:
                self.winner = "MAFIA"
                self.state = "S" # Sort and make string
            elif "TOWN WINS" in line:
                self.winner = "TOWN"
                self.state = "S" # Sort and make string

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

        self.score = BASE_SCORE
        for role in self.role_dict:
            self.score += ROLE_SCORES[role] * self.role_dict[role]

        self.desc = ""

        for role in ("TOWN","COP","DOCTOR","CELEB","IDIOT","MAFIA","GODFATHER"):
            self.desc += role + ":" + str(self.role_dict[role]) + ","

class Records:

    def __init__(self, path):
        try:
            f = open(path,'r')
        except:
            print("Couldn't open path")
            exit()

        newGame = Game_Record(f)
        self.game_dict = {}
        self.game_list = []

        while not newGame.state == "N":
            if not newGame.desc in self.game_dict:
                self.game_dict[newGame.desc] = (0,0)

            if newGame.winner == "TOWN":
                self.game_dict[newGame.desc] = (self.game_dict[newGame.desc][0]+1,
                                                self.game_dict[newGame.desc][1])
            elif newGame.winner == "MAFIA":
                self.game_dict[newGame.desc] = (self.game_dict[newGame.desc][0],
                                                self.game_dict[newGame.desc][1]+1)
            else:
                print("GAME WITHOUT PROPER WINNER")
            self.game_list.append(newGame)
            newGame = Game_Record(f)

        numbers_dict = {}
        for g in self.game_list:
            nums = (g.town_num, g.maf_num)
            if not nums in numbers_dict:
                numbers_dict[nums] = (0,0)
            if g.winner == "TOWN":
                numbers_dict[nums] = (numbers_dict[nums][0]+1,numbers_dict[nums][1])
            if g.winner == "MAFIA":
                numbers_dict[nums] = (numbers_dict[nums][0],numbers_dict[nums][1]+1)
        self.numbers_dict = numbers_dict

if __name__ == "__main__":
    #if len(sys.argv) <= 1:
    #    print("Specify file name")
    #    exit()

    path = "data/records" #sys.argv[1]

    records = Records(path)
