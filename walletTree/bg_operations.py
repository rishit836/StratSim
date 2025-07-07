from threading import Thread
import time
import os
import datetime
from .modelling import train


global mod ,file_counter,file_name

file_counter = 0
file_name=None
def watchdog(t):
    global mod,watchdog_status
    print("watchdog is runnning")
    watchdog_status=True
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
    global mod, file_counter,training_status
    training_status = True
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
    
    if not watchdog_status:
        print("watchdog is enabled")
        watchdog_thread = Thread(target=watchdog, args=(ticker,))
        watchdog_thread.start()
        
        

    else:
        print("already runnning no need for starting another subprocess for watchdog")

    if not training_status:
        print("second process started")
        training_model_thread = Thread(target=rl_model_train,args=(ticker,data_len,))
        training_model_thread.start()
    else:
        print("already running no need for starting another subprocess for training ")




    



if __name__ == "__main__":
    print("Debug Mode:")
    bg_handler("NVDA")
