from MController import MController

import time
from MComm import TestMComm
from MRecord import PrintMRecord

ctrl = MController("lobby",["group1","group2"],TestMComm, PrintMRecord)
ctrl.command("lobby","0","1",{'text':"/start 1 5"})
ctrl.lobbyComm.acks = ['1','2','3','4','5']
ctrl.determined_roles = ["TOWN","TOWN","TOWN","TOWN","MAFIA"]
ctrl.command("lobby","1","1",{'text':"/status"})
ctrl.command("lobby","1","1",{'text':"/extend -1"})
time.sleep(3)
ctrl.command("group2","1","1",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
ctrl.command("group2","1","3",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
ctrl.command("group2","1","4",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
