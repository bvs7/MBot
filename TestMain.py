# TestMain

from MInfo import *
from MState import MState
from MComm import MComm

if __name__ == "__main__":

    lobby = MComm("lobby")

    main = MComm("main")
    maf = MComm("maf")

    m = MState(['1','2','3','4','5'], main, maf, lobby)

    
    

    
