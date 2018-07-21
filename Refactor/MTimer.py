import time
import threading

class MTimer:
    """Used to create a timer object and bind functions to specific times for it"""
    
    def __init__(self, value, alarms={}, id=None):
        """ value is the starting time value in seconds
        alarms is a dict mapping a second value to a list of alarm functions
        id is to help with debugging """
        self.value = value
        self.alarms = alarms
        self.active = True
        
        self.lock = threading.Lock()
        
        self.timerThread = threading.Thread(name="Timer"+str(id), target=self.tick)
        self.timerThread.start()
        
    def tick(self):
        while self.active:
            
            self.lock.acquire()
            for value,actions in self.alarms.items():
                if self.value == value:
                    self.lock.release()
                    for action in actions:
                        action()
                    self.lock.acquire()
            if self.value == 0:
                self.lock.release()
                self.active = False
                return
            self.value -= 1
            self.lock.release()
            time.sleep(1)
            
    def addAlarms(self, alarms):
        with self.lock:
            for value,actions in alarms:
                if not value in self.alarms:
                    self.alarms[value] = []
                for action in actions:
                    self.alarms[value].append(action)
            
    def getTime(self):
        with self.lock:
            if not self.active:
                return None
            return self.value
            
    def addTime(self, seconds):
        with self.lock:
            if not self.active:
                return None
            self.value += seconds
            if self.value < 0:
                self.value = 0
                
    def halt(self):
        with self.lock:
            self.active = False
            self.alarms = {}
            self.value = 0
            
    
    def __str__(self):
        return time.strftime("%H:%M:%S",time.gmtime(self.value))