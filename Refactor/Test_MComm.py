
import MComm

DEBUG_GROUP_ID = '40222842'
BRIAN_USER_ID = '21642197'

if not MComm.groupy_imported:
    print("Test failed because groupy not imported")

debug_group = MComm.GroupComm(DEBUG_GROUP_ID)

m_id = debug_group.cast("TestCast")

debug_group.ack(m_id)

debug_group.send("TestSend", BRIAN_USER_ID)