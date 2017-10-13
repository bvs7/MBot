
import random

class Role_Generator:

    def __init__(self, pref):
        self.pref = pref

    def genRoles(self, num):
        return ["TOWN"] * num

class Score_RG(Role_Generator):

    def __init__(self, base, role, weights, pref):
        Role_Generator.__init__(pref)
        self.base_score = base
        self.role_scores = role
        self.weights = weights

    def genRoles(self, num_players):

        assert(numplayers >= 3, "Too few players")

        while(True):
            n = 0
            score = self.base_score
            roles = []
            num_mafia = 0
            num_town = 0
            num_idiot = 0
            town_sum = sum(self.weights[1])
            mafia_sum = sum(self.weights[3])
            role = "TOWN"

            if self.pref.book["standard_roles"] == "COP_DOC":
                roles = ["COP","DOCTOR"]
                num_town = 2
                n = 2
                score += ROLE_SCORES["COP"] + ROLE_SCORES["DOCTOR"]

            if num_players == 4:
                return ["TOWN", "DOCTOR", "COP", "MAFIA"]
            elif num_players == 3:
                return ["DOCTOR", "MAFIA", "COP"]
            while(n < num_players):
                if score < 0:
                    # Add Town
                    t = random.randint(0,town_sum)
                    for i in range(len(self.weights[0])):
                        if t < sum(self.weights[1][0:(i+1)]):
                            role = self.weights[0][i]
                            break
                    num_town += 1
                else:
                    # Add Mafia
                    m = random.randint(0,mafia_sum)
                    for i in range(len(self.weights[2])):
                        if m < sum(len(self.weights[3][0:(i+1)])):
                            role = self.weights[2][i]
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

            # Done making roles, ensure this isn't a bad game
            if not ((num_mafia + num_idiot + 2 >= num_town) or (num_mafia == 0)):
                break

        # Roles contains a valid game
        return roles

class Fancy_Score_Generator(Role_Generator):
    def __init__(self, base, roles, weights, pref):
        Role_Generator.__init__(pref)
        self.base_score = base
        self.role_scores = roles
        self.town_weights = self.weights[0:2]
        self.maf_weights = self.weights[2:4]

    def genRoles(self, num):

        

}
