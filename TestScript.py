import GroupyComm
import MState

c = GroupyComm.GroupyCommTest()
m = MState.MState(c)

m.nextPlayerIDs = ["1","2","3","4","5","6","7"]

m.startGame()

