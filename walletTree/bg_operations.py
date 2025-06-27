from multiprocessing import Process
import time
import os
import datetime

def watchdog(t):
    print("watchdog is runnning")
    path = 'data/'+t
    
    try:
        last_modified = os.path.getmtime(path)
        watchdog_start_time = datetime.datetime.now()
        time_to_run = datetime.timedelta(minutes=15)
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
            last_modified = current_modified



def rl_model_train():
    print("finished training")

def bg_handler(ticker):
    print("watchdog is enabled")
    watchdog_process = Process(target=watchdog,args=(ticker,))
    watchdog_process.start()
    print("second process started")
    training_model_process = Process(target=rl_model_train)
    training_model_process.start()

    watchdog_process.join()
    training_model_process.join()



    



if __name__ == "__main__":
    print("Debug Mode:")
    bg_handler("NVDA")
