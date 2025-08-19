from django.shortcuts import render,HttpResponse
from django.http import JsonResponse

# Create your views here.
import random
import os
from dotenv import load_dotenv
import requests
import pandas as pd
import yfinance as yf
import threading
from .bg_operations import bg_handler,wait_clock
from stocks.views import chart_view
from django.core.cache import cache
from .indicators import compute_indicators


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
    # for now
    '''
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
    '''
    print("Data Already exists or fetched.")

def get_data_for_view(ticker,period:str="1y"):
    try:
        t = yf.Ticker(ticker=ticker)
        if period =="1d":
            data = t.history(period=period,interval="1m")
        else:
            data = t.history(period=period)
        
        # Check if DataFrame is empty
        if data.empty:
            return False
            
        df = pd.DataFrame(data)
        _result_ = compute_indicators(df)
        df['date'] = pd.to_datetime(df.index)
        if period == "1y":
            df['date']=df['date'].dt.strftime("%d-%m-%y")
        if period == "1d":
            df['date']=df['date'].dt.strftime("%H:%M:%S")
        df.reset_index(inplace=True)
        name = str(ticker) + "_"+period
        for keys in _result_.keys():
            df[str(keys)] = _result_[keys]
        print(df.head())
        cache.set(name,df,timeout=60*60*24)
        cache.set(str(period)+"_result",_result_, timeout=60*60*24)
        return True
    except Exception as e:
        print(f"Error getting data: {e}")
        return False
    
global data_loaded

data_loaded = False
def retrieve_data(ticker):
    global data_loaded
    d_lst = ['1d', '5d', '1mo',  'max']
    for period in d_lst:
        stat = get_data_for_view(ticker,period)
        if not stat:
            print("error getting data for",ticker,"for period:",period)
            return False
    data_loaded = True


def scrape(request,ticker):
    global t,status,data_loaded
    chart_view = cache.get("chart_view")
    name = str(ticker) + "_"
    

    if not cache.get("data_name") == name:
        data_loaded = False
        print("new ticker data loaded.")
        cache.set("data_name",name,timeout=60*60*24)
        cache.set("chart_view","one-year",timeout=60*60*24)

    d_lst = ['1d', '5d', '1mo',  'max']
    cache.set("data_name",name,timeout=60*60*24)
    c= {}
    if not data_loaded:
        stat = get_data_for_view(ticker)
        view_data_thread = threading.Thread(target=retrieve_data, args=[ticker,], name="view_data_retrieve")
        view_data_thread.start() 

    # if os.path.exists("models/"+ticker+"_model.pkl"):
    #     status = True
    # else:
    #     status= False
    status= True
    t = ticker.upper()
    if not "test_clock" in wait_clock.get_names():
        clock_obj = wait_clock("test_clock")
        threading.Thread(target=clock_obj.start_clock).start() 
    else:
        clock_obj = wait_clock.get_objects()[0]
    expected_time = clock_obj.time_now()
    if not status:
        t = ticker.upper()
        ticker = yf.Ticker(t)
        data = ticker.history(period="1y")
        expected_time = (len(data['Close'])/5)*60
        # expected_time = 3000
        handler_running = False
        for th in threading.enumerate():
            if th.name =="handler":
                handler_running = True
        if not handler_running:
            bg_op_thread = threading.Thread(target=bg_handler,name="handler",args=(t,len(data['Close']),))
            bg_op_thread.start()
        c.update({"time":expected_time})
    c.update({"data_1y":cache.get(name+"1y")})
    c.update({"result_1y":cache.get("1y_result")})

    c.update({"time":expected_time})

    if data_loaded:
        for period in d_lst:
            c.update({"data_"+period:cache.get(name+period)})
            c.update({"result_"+period:cache.get(str(period)+"_result")})
    c.update({"ticker":t.upper()})
    c.update({"active_view":chart_view})
    with open("loading_context.txt","w") as f:
        f.write(str(c))
    return render(request,"loading.html",context=c)
    


def chart_data(request):
    chart_view = cache.get("chart_view")
    name = cache.get("data_name")
    period_code = None  # track period string used for indicators cache key
    if chart_view.lower() == "one-day":
        d = cache.get(name+"1d")
        period_code = "1d"
        data = {
                "labels": d['date'].to_list(),
                "values": d['Close'].to_list()
            }
    if chart_view.lower() == "one-year":
        d = cache.get(name+"1y")
        period_code = "1y"
        data = {
                "labels": d['date'].to_list(),
                "values": d['Close'].to_list()
            }
    if chart_view.lower() == "one-week":
        d = cache.get(name+"5d")
        period_code = "5d"
        data = {
                "labels": d['date'].to_list(),
                "values": d['Close'].to_list()
            }
    if chart_view.lower() == "one-month":
        d = cache.get(name+"1mo")
        period_code = "1mo"
        data = {
                "labels": d['date'].to_list(),
                "values": d['Close'].to_list()
            }
    if chart_view.lower() == "max":
        d = cache.get(name+"max")
        period_code = "max"
        data = {
                "labels": d['date'].to_list(),
                "values": d['Close'].to_list()
            }
    if data is None:
        return JsonResponse({"error": "Error Fetching Data"}, status=400)

    # Append indicators (minimal backend change): pull cached result dict
    indicators_payload = []
    if period_code:
        result_dict = cache.get(period_code+"_result")
        if result_dict:
            try:
                for k, v in result_dict.items():
                    # v expected to be a pandas Series
                    try:
                        indicators_payload.append({
                            "name": k,
                            "data": [None if pd.isna(x) else float(x) for x in v.tolist()]
                        })
                    except Exception:
                        pass
            except Exception:
                pass
    data["indicators"] = indicators_payload
    return JsonResponse(data)



def home(request):
    return HttpResponse("Hello!, This is a breakdown app")


