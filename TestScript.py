import GroupyComm
import MState

c = GroupyComm.GroupyCommTest()
m = MState.MState(c)

m.nextPlayerIDs = ["1","2","3","4","5","6","7","8","9","10","11","12","13","14","15","16","17"]

m.startGame()

m.vote("1","2")
m.vote("3","2")
m.vote("4","2")
m.vote("5","2")
m.vote("6","2")
m.vote("7","2")
m.vote("8","2")
m.vote("9","2")
m.vote("10","2")
