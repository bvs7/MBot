#!/usr/bin/python3

import sys

SCORES = [
    (-8,
     {
         "MAFIA"    : -3,
         "GODFATHER" : -3,
         "DOCTOR" :    4,
         "COP"        :    4,
         "TOWN"     :    2,
         "IDIOT"    : -2,
         "CELEB"    :    3,
     }),
    (-9,
     {
         "MAFIA"    : -2,
         "GODFATHER" : -2,
         "DOCTOR" :    4,
         "COP"        :    4,
         "TOWN"     :    2,
         "IDIOT"    : -2,
         "CELEB"    :    3,
     }),
    (-9,
     {
         "MAFIA"    : -3,
         "GODFATHER" : -3,
         "DOCTOR" :    4,
         "COP"        :    4,
         "TOWN"     :    2,
         "IDIOT"    : -2,
         "CELEB"    :    3,
     }),
]

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
        self.roles = []
        while self.state == "R":
            line = f.readline()
            for role in ("TOWN", "MAFIA", "COP", "DOCTOR", "GODFATHER", "IDIOT", "CELEB"):
                if role in line:
                    self.roles.append(role)
                    if role in ("TOWN","COP","DOCTOR","CELEB"):
                        self.town_num += 1
                    elif role in ("MAFIA","GODFATHER"):
                        self.maf_num += 1
                    elif role == "IDIOT":
                        self.idiot_num += 1
                    break
            if "Game Begins" in line:
                self.state = "W" # look for winner

        for role in self.roles:
            self.role_dict[role] += 1

        while self.state == "W":
            line = f.readline()
            if "MAFIA WINS" in line:
                self.winner = "MAFIA"
                self.state = "S" # Sort and make string
            elif "TOWN WINS" in line:
                self.winner = "TOWN"
                self.state = "S" # Sort and make string

    def getDesc(self):
        desc = ""

        for role in ("TOWN","COP","DOCTOR","CELEB","IDIOT","MAFIA","GODFATHER"):
            desc += role + ":" + str(self.role_dict[role]) + ","
        return desc

    def genScore(self,base_score,gf_c_deduct,role_scores):
        score = base_score
        for role in self.roles:
            score += role_scores[role]
            if role == "COP":
                score -= len([None for g in self.roles if g == "GODFATHER"]) * gf_c_deduct
            if role == "GODFATHER":
                score -= len([None for c in self.roles if c == "COP"]) * gf_c_deduct
        return score

    def scoreJudgePoints(self,score):
        if score >= 0 and self.winner == "TOWN":
            return 0
        if score <= 0 and self.winner == "MAFIA":
            return 0
        return score

class Records:

    def __init__(self, path):
        try:
            f = open(path,'r')
        except:
            print("Couldn't open path")
            exit()

        newGame = Game_Record(f)
        self.game_list = []

        while not newGame.state == "N":
            self.game_list.append(newGame)
            newGame = Game_Record(f)

    def getNums(self):
        numbers_dict = {}
        for g in self.game_list:
            nums = (g.town_num, g.maf_num)
            if not nums in numbers_dict:
                numbers_dict[nums] = (0,0)
            if g.winner == "TOWN":
                numbers_dict[nums] = (numbers_dict[nums][0]+1,numbers_dict[nums][1])
            if g.winner == "MAFIA":
                numbers_dict[nums] = (numbers_dict[nums][0],numbers_dict[nums][1]+1)
        return numbers_dict

    def genPoints(self,scores,fn):
        points = 0
        for g in self.game_list:
            s = g.genScore(scores[0],scores[1],scores[2])
            p = fn(g.scoreJudgePoints(s))
            points += p
        return points

if __name__ == "__main__":
    #if len(sys.argv) <= 1:
    #    print("Specify file name")
    #    exit()

    path = "data/records" #sys.argv[1]

    records = Records(path)
