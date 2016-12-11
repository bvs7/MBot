import GroupyComm
import MState

c = GroupyComm.GroupyCommTest()
m = MState.MState(c)

m.nextPlayerIDs = ["1","2","3","4","5"]

m.startGame()

m.vote("1","2")
m.vote("3","2")
m.vote("4","2")
