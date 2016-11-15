import GroupyComm
import MState

c = GroupyComm.GroupyCommTest()
m = MState.MState(c)

m.nextPlayerIDs = ["1","2","3","4","5","6","7","8","9","10","11"]

m.startGame()

m.vote("1","2")
m.vote("3","2")
m.vote("4","2")
m.vote("5","2")
m.vote("2","2")
m.vote("6","2")
