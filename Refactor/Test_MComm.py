#!/usr/bin/python3

import MComm

DEBUG_GROUP_ID = '40222842'
BRIAN_USER_ID = '21642197'

if not MComm.groupy_imported:
    print("Test failed because groupy not imported")

debug_group = MComm.GroupComm(DEBUG_GROUP_ID)

#for i in range(20):
#  m_id = debug_group.cast("TestCast {}".format(i))
#  debug_group.ack(m_id)

#for i in range(20):
#  print(debug_group.send("TestSend {}".format(i), BRIAN_USER_ID))

print(debug_group.getName(BRIAN_USER_ID))

#print(debug_group.getAcks(m_id))

debug_group.add(BRIAN_USER_ID)

debug_group.clear([BRIAN_USER_ID])

debug_group.clear()

debug_group.add(BRIAN_USER_ID, "Brian Scaramella")
