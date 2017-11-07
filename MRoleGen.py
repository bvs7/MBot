# Different Game Generation techniques

import random

from MInfo import *
import MState


def genRolesRandom(num_players):
    """ Create a list of roles of length num_players. Totally randomized but follows a few rules """
    assert(num_players >= 3)
    if num_players == 3:
        return ["COP","DOCTOR","MAFIA"]
    elif num_players == 4:
        return ["COP","DOCTOR","STRIPPER","CELEB"]

    while(True):
        n = 0
        roles = []
        num_maf = 0
        num_town = 0
        num_rogue = 0
        odds_sum = sum(ALL_WEIGHTS[1])
        while(n < num_players):
            acc = 0
            r = random.randint(1,odds_sum)
            for i in range(len(ALL_WEIGHTS[0])):
                acc += ALL_WEIGHTS[1][i]
                if r <= acc:
                    role = ALL_WEIGHTS[0][i]
                    roles.append(role)
                    n += 1
                    if role in TOWN_ROLES:
                        num_town += 1
                    elif role in MAFIA_ROLES:
                        num_maf += 1
                    elif role in ROGUE_ROLES:
                        num_rogue += 1
                    break
        if (not num_town > num_maf+2) or (not num_maf > 0):
            continue
        break
    return roles

def genRolesScores(num_players, scores=ROLE_SCORES, weights=ALL_WEIGHTS):
    """ Create a list of roles of length num_players. Uses randomish but semi-fair assignment """
    assert(num_players >= 3)
    while(True):
        n = 0
        score = BASE_SCORE
        roles = []
        num_maf = 0
        num_town = 0
        num_rogue = 0
        pro_town = ALL_WEIGHTS[0:2]
        anti_town = ALL_WEIGHTS[2:4]

        if num_players == 4:
            return ["CELEB", "DOCTOR", "COP", "STRIPPER"]
        elif num_players == 3:
            return ["DOCTOR", "MAFIA", "COP"]
        while(n < num_players):
            acc = 0
            if score < 0:
                t = random.randint(1,town_sum)
                for i in range(len(pro_town[0])):
                    acc += pro_town[1][i]
                    if t <= acc:
                        role = TOWN_WEIGHTS[0][i]
                        break
            else:
                m = random.randint(1,mafia_sum)
                for i in range(len(anti_town[0])):
                    acc += anti_town[1][i]
                    if m <= acc:
                        role = anti_town[0][i]
                        break
            if role in TOWN_ROLES:
                num_town += 1
            elif role in MAFIA_ROLES:
                num_maf += 1
            elif role in ROGUE_ROLES:
                num_rogue += 1

            roles.append(role)
            score += scores[role]
            # Special Rules?
            n += 1

        if pref.book["standard_roles"] == "COP_DOC":
            if len([c for c in roles if c == "COP"]) < 1 or len([d for d in roles if d == "DOCTOR"]) < 1:
                continue # Try generating again. Until we have a game with COP and DOC...

        # Done making roles, ensure this isn't a bad game
        if (not num_town >= num_maf+2) or (not num_maf > num_players/6):
            continue

    # Roles contains a valid game
    return roles


def addRoleScore(score,pro_town,anti_town):
    town_sum = sum(pro_town[1])
    anti_sum = sum(anti_town[1])
    acc = 0
    if score < 0:
        t = random.randint(1,town_sum)
        for i in range(len(pro_town[0])):
            acc += pro_town[1][i]
            if t <= acc:
                role = pro_town[0][i]
                break
    else:
        m = random.randint(1,anti_sum)
        for i in range(len(anti_town[0])):
            acc += anti_town[1][i]
            if m <= acc:
                role = anti_town[0][i]
                break

    return role

def genScoreMatrix(roles, matrix=SCORE_MATRIX, pref=None):
    score = matrix["BASE"] #Start with base score
    if pref == None:
        pref = MState.Preferences()
    # Base scores of rules
    for rule in pref.book:
        if rule in SCORE_ROLES:
            score += matrix[rule][pref.book[rule]]

    for i in range(len(roles)):
        role = roles[i]
        score += matrix[role]["BASE"] # Add a base score
        for j in range(len(roles)):
            if not i == j:
                other = roles[j]
                score += matrix[role][other] # Add synergy score
        for rule in pref.book:
            if rule in SCORE_ROLES:
                score += matrix[role][rule][pref.book[rule]] # Add rule synergy score

    return score


def genRolesMatrix(num_players, matrix=SCORE_MATRIX, pref=None):
    """ Iterate: add a player then recalculate score """
    assert(num_players >= 3)
    if pref == None:
        pref = MState.Preferences()

    if num_players < 7:
        return genRolesRandom(num_players)
    while(True):
        roles = []
        n = 0
        num_maf = 0
        num_town = 0
        num_rogue = 0
        pro_town = TOWN_WEIGHTS
        anti_town = MAFIA_WEIGHTS

        extra_cop = False
        if "COP" in pref.book["standard_roles"]:
            roles.append("COP")
            num_town += 1
            n+=1
            extra_cop = True
        extra_doc = False
        if "DOC" in pref.book["standard_roles"]:
            roles.append("DOCTOR")
            num_town += 1
            n += 1
            extra_doc = True


        while(n < num_players):
            score = genScoreMatrix(roles,matrix)

            role = addRoleScore(score,pro_town,anti_town)

            if extra_cop and role == "COP":
                extra_cop = False
                role = "TOWN"
            if extra_doc and role == "DOCTOR":
                extra_cop = False
                role = "TOWN"

            roles.append(role)

            if role in TOWN_ROLES:
                num_town += 1
            elif role in MAFIA_ROLES:
                num_maf += 1
            elif role in ROGUE_ROLES:
                num_rogue += 1

            n += 1

        # Change roles if some aren't necessary
        # If no MAF|STR: COP -> TOWN
        # If no COP: GDF -> MAF | MLR -> TOWN
        # If no COP|DOC|CLB: STR -> MAF
        if (not "MAFIA" in roles) and (not "STRIPPER" in roles) and (not "MILLER" in roles):
            while True:
                try:
                    roles.remove("COP")
                    roles.append("TOWN")
                except:
                    break

        if not "COP" in roles:
            while True:
                try:
                    roles.remove("GODFATHER")
                    roles.append("MAFIA")
                except:
                    break
            while True:
                try:
                    roles.remove("MILLER")
                    roles.append("TOWN")
                except:
                    break

        if (not "COP" in roles) and (not "DOCTOR" in roles) and (not "CELEB" in roles):
            while True:
                try:
                    roles.remove("STRIPPER")
                    roles.append("MAFIA")
                except:
                    break

        diff = num_town - num_maf
        ratio = num_maf/num_players
        score = genScoreMatrix(roles,matrix)
        if diff <= 2 or ratio < 0 or ratio >= .4 or score < -25 or score > 25 :
            continue
        else:
            break

    print(genScoreMatrix(roles,matrix))
    return roles
