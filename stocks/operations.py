import finnhub
import dotenv
import pandas as pd
import datetime as dt
import time
import pickle
import os
key = dotenv.get_key(".env","finhub_api")

def delete_if_outdated(filepath, max_age_seconds=60*60*24):
    if os.path.exists(filepath):
        last_modified_time = os.path.getmtime(filepath)
        
        current_time = time.time()
        if current_time - last_modified_time > max_age_seconds:
            os.remove(filepath)
            print(f"Deleted {filepath} (outdated)")
        else:
            print(f"{filepath} is still valid")
    else:
        print(f"{filepath} does not exist")
def create_sector(filepath="data.csv")->dict:
    if not os.path.exists(filepath):
        return "False"
    fnb_client = finnhub.Client(key)
    df = pd.read_csv(filepath)
    if not os.path.exists('sectors.dat'):
        sectors = {}
    else:
        sectors = pickle.load(open('sectors.dat',"rb"))
    request_num = 0
    now_time = dt.datetime.now()
    limit_time = now_time + dt.timedelta(minutes=1)
    for num,row in df.iterrows():
            if row['symbol'] not in sectors.keys():
                if not (limit_time - now_time).total_seconds() <1 and ( request_num <=59) : 
                    response = fnb_client.company_profile2(symbol=row['symbol'])
                    request_num += 1
                    if "finnhubIndustry" in response:
                        sectors.update({row['symbol']:response['finnhubIndustry']})
                else:
                    print('limit reached please wait for ',(limit_time-now_time).total_seconds())
                    request_num = 0 
                    now_time = dt.datetime.now()
                    time.sleep((limit_time-now_time).total_seconds()+3)
                    limit_time = now_time + dt.timedelta(minutes=1)
    sec_dict = sectors
    with open('sectors.dat',"wb") as f:
        pickle.dump(sectors,f)
    
    return sec_dict




