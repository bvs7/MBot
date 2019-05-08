from MController import MController

import time
from MComm import TestMComm
from MRecord import PrintMRecord

ctrl = MController(["lobby"],["group1","group2"],TestMComm, PrintMRecord)
ctrl.command("start", "lobby","0","1",{'text':"/start 1 5"})
ctrl.lobbys["lobby"].comm.acks = ['1','2','3','4','5']
ctrl.lobbys["lobby"].determined_roles = ["TOWN","TOWN","TOWN","TOWN","MAFIA"]
ctrl.command("status","lobby","1","1",{'text':"/status"})
ctrl.command("extend","lobby","1","1",{'text':"/extend -1"})
time.sleep(3)
ctrl.command("vote", "group2","1","1",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
ctrl.command("vote", "group2","1","3",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
ctrl.command("vote", "group2","1","4",{"text":"/vote @ansdbfa", "attachments":[{"type":"mention",'user_ids':['5']}]})
