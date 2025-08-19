from threading import Thread
import threading
import time
import os
import datetime
from .modelling import train



global mod ,file_counter,file_name

file_counter = 0
file_name=None
def watchdog(t):
    global mod
    print("watchdog is runnning")
    path = 'data/'+t
    
    try:
        last_modified = os.path.getmtime(path)
        watchdog_start_time = datetime.datetime.now()
        time_to_run = datetime.timedelta(minutes=50)
        end_time = watchdog_start_time + time_to_run
        
    except FileNotFoundError:
        print("Internal Error Occured Maybe the data scraping hasnt started yet")
    while True:
        current_time = datetime.datetime.now()
        if ( end_time - current_time).seconds < 1:
            print("Watchdog Shutting Down..")
            break
        else:
            current_modified = os.path.getmtime(path)
            if current_modified != last_modified:
                print("Folder Was Modified, i.e new data was stored")
                mod = True
            last_modified = current_modified



def rl_model_train(ticker,data_len):
    global mod, file_counter
    mod = [False] * data_len
    training = False
    
    # while all the files havent been used for training
    while not all(mod):
        if not training:
            training = train(file_counter,file_name)
        
        

    
    print("finished training")

global watchdog_status,training_status
watchdog_status = False
training_status = False

def bg_handler(ticker,data_len):
    global mod,file_counter,watchdog_status,training_status


    
    for th in threading.enumerate():
        if th.name == "custom_watchdog":
            watchdog_status = True
        if th.name == "rl_model_train":
            training_status = True
    if not watchdog_status:
        watchdog_thread = Thread(target=watchdog,name="custom_watchdog", args=(ticker,))
        watchdog_thread.start()
        
    else:
        print("already runnning no need for starting another subprocess for watchdog")

    if not training_status:
        print("second process started")
        training_model_thread = Thread(target=rl_model_train,name="rl_model_train",args=(ticker,data_len,))
        training_model_thread.start()
        
    else:
        print("already running no need for starting another subprocess for training ")


class wait_clock():
    _instances = []
    _names = []
    def __init__(self,name:str,time:int=3000):
        self.time = time
        #creating a time copy
        self.current_time = self.time # so that can reduce the timer
        self.timer_started = False
        wait_clock._names.append(name)
        wait_clock._instances.append(self)

    
    def time_now(self):
        return self.current_time
    
    def timer_is_done(self):
        if self.current_time <=0 :
            return True
        else:
            return False
    
    def start_clock(self):
        if not self.timer_started:
            while self.current_time > 0:
                self.current_time -= 1
                time.sleep(1)
        else:
            print("Clock already running time left is:",self.current_time)

    @classmethod
    def get_objects(cls):
        return cls._instances

    @classmethod
    def get_names(cls):
        return cls._names
    








if __name__ == "__main__":
    print("Debug Mode:")
    bg_handler("NVDA")
