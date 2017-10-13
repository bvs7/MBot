
import RecordParser

records = RecordParser.Records("data/records")

champ = (-8, 1,{
        "MAFIA"    : -3,
        "GODFATHER" : -3,
        "DOCTOR" :    4,
        "COP"        :   4,
        "TOWN"     :    2,
        "IDIOT"    : -2,
        "CELEB"    :    3,
})

def my_abs(a):
    if a < 0:
        return -a
    return a

def my_sq(a):
    return a*a

def try_sq(a):
    return abs(a)*a*a

def sq_sq(a):
    return a*a*a*a

def try_this(a):
    b = my_abs(a)
    return (b+1)/2

champ_score = records.genPoints(champ,try_sq)

for base in range(-12,-4):
    print("Progress",base)
    for gf_c in range(0,3):
        for maf in range(-6,-2):
            for doc in range(2,7):
                for cop in range(2,7):
                    for town in range(0,4):
                        for idiot in range(-5,0):
                            for celeb in range(0,6):
                                scores = (base,gf_c,{
                                    "MAFIA":maf,
                                    "GODFATHER":maf,
                                    "DOCTOR":doc,
                                    "COP":cop,
                                    "TOWN":town,
                                    "IDIOT":idiot,
                                    "CELEB":celeb,
                                })

                                score = records.genPoints(scores,my_sq)

                                if score < champ_score:
                                    print("gottem")
                                    champ_score = score
                                    champ = scores

print(champ)
