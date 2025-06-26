from django.shortcuts import render,HttpResponse

# Create your views here.
import random
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import yfinance as yf
import threading

global status

def fetch_data(date, ticker, interval="1"):
    """
    Fetch intraday OHLCV data for a given stock on a specific date and interval.
    
    Parameters:
        date (str): Date in 'YYYY-MM-DD' format
        ticker (str): Stock ticker (e.g., 'AAPL')
        interval (str): Time interval in minutes (e.g., '1', '5', '15')
    
    Returns:
        pd.DataFrame: DataFrame with timestamp, open, high, low, close, volume
    """
    load_dotenv()
    api_key = os.getenv("polygon_api")
    
    if not api_key:
        raise ValueError("API key not found. Please set 'polygon_api' in your .env file.")
    
    valid_intervals = {"1", "5", "15", "30", "60"}
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval '{interval}'. Choose from {valid_intervals}.")

    url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/{interval}/minute/{date}/{date}"
    params = {
        "adjusted": "true",
        "sort": "asc",
        "limit": 50000,
        "apiKey": api_key
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        print("Data Not Found")
        print(response)
        return None, False
    
    json_data = response.json()
    results = json_data.get("results", [])

    if not results:
        print(f"No data found for {ticker} on {date}.")
        return pd.DataFrame()

    # Convert to DataFrame
    df = pd.DataFrame(results)
    df['timestamp'] = pd.to_datetime(df['t'], unit='ms')
    df.rename(columns={
        'o': 'open',
        'h': 'high',
        'l': 'low',
        'c': 'close',
        'v': 'volume'
    }, inplace=True)
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    return df,True
    
import time
from datetime import datetime
import datetime as dt
def get_data(data):
    global t
    request_num = 0
    # polygon api limits 5apicall/minute
    now_time = datetime.now()
    time_limit = now_time + dt.timedelta(minutes=1)
    for date in data['date']:
        if not os.path.exists('data/'+t+"/"+t+"_"+str(date)+".csv"):
            if request_num <5 and ((time_limit - datetime.now()).seconds > 0):
                df,status = fetch_data(date,t,"5")
                if status:
                    request_num+=1
                    df.to_csv('data/'+t+"/"+t+"_"+str(date)+".csv",index=False)
                    print("data_saved")
                else:
                    print("data was none")
            elif request_num == 5 or ((time_limit - datetime.now()).seconds <= 0):
                request_num = 0
                now_time = datetime.now()
                time_limit = now_time + dt.timedelta(minutes=1)
                print("time limit reached or max request reached")
                print("wait till", time_limit, "that is",str((time_limit - datetime.now())))
                time.sleep( (time_limit - datetime.now()).seconds + 1)
        else:
            print(date, "exists")

    print("Data Already exists or fetched.")

def scrape(request,ticker):
    global t,status
    c= {}

    # if os.path.exists("models/"+ticker+"_model.pkl"):
    #     status = True
    # else:
    #     status= False
    status= False
    if not status:
        t = ticker.upper()
        ticker = yf.Ticker(t)
        data = ticker.history(period="1y")
        expected_time = (len(data['Close'])/5)*60

        c.update({"time":expected_time})
        # data['date'] = data.index
        # data.reset_index(inplace=True,drop=True)
        # data['date'] = pd.to_datetime(data['date'])
        # data['date'] = data['date'].dt.strftime('%Y-%m-%d')
        # threading.Thread(target=get_data,args=[data]).start()
    c.update({"ticker":t.upper()})
    return render(request,"loading.html",context=c)
    



def home(request):
    return HttpResponse("Hello!, This is a breakdown app")


