import time
import threading

class MTimer:
    """Used to create a timer object and bind functions to specific times for it"""
    
    def __init__(self, limit, callbacks={}, id=None):
        """ limit is the starting time limit in seconds
        callbacks is a dict mapping a second value to a list of callback functions
        id is to help with debugging """
        self.limit = limit
        self.callbacks = callbacks
        self.active = True
        
        self.lock = threading.Lock()
        
        self.timerThread = threading.Thread(name="Timer"+str(id), target=self.tick)
        self.timerThread.start()
        
    def tick(self):
        while self.active:
            
            self.lock.acquire()
            for limit,actions in self.callbacks.items():
                if self.limit == limit:
                    self.lock.release()
                    for action in actions:
                        action()
                    self.lock.acquire()
            if self.limit == 0:
                self.lock.release()
                self.active = False
                return
            self.limit -= 1
            self.lock.release()
            time.sleep(1)
            
    def addCallbacks(self, callbacks):
        with self.lock:
            for limit,actions in callbacks:
                if not limit in self.callbacks:
                    self.callbacks[limit] = []
                for action in actions:
                    self.callbacks[limit].append(action)
            
    def getTime(self):
        with self.lock:
            if not self.active:
                return None
            return self.limit
            
    def addTime(self, seconds):
        with self.lock:
            if not self.active:
                return None
            self.limit += seconds
            if self.limit < 0:
                self.limit = 0
                
    def halt(self):
        with self.lock:
            self.active = False
            self.callbacks = {}
            self.limit = 0
            
    
    def __str__(self):
        return time.strftime("%H:%M:%S",time.gmtime(self.limit))