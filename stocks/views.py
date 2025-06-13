from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.db.models import Q
import pandas as pd
import yfinance as yf
import os
import threading
from django.core.cache import cache
from django.http import JsonResponse
from django.urls import reverse
import random

# Global flags
filter_applied = False
list_cat = "top"
filter_cat = None
data_generated = False
cat_map = {
    "top":"TOP 100",
    "mostactive":"MOST ACTIVE",
    "trend":"TRENDING"
}

def get_chart_data(ticker):
    ticker = yf.Ticker(ticker)
    d = ticker.history(period='1mo')
    d['Date'] = d.index
    d['Date'] = d['Date'].dt.tz_convert('Asia/Kolkata').dt.strftime('%d/%m/%Y')
    d.reset_index(drop=True,inplace=True)
    cache.set('data_dict',d,timeout=60*60*24)
    return d


def generate_data(d):
    response = yf.screen(d)
    symbols,names,current_price,price_change,percent_change = [], [],[],[],[]
    for data in response['quotes']:
        symbols.append(data['symbol'])
        names.append(data['longName'])
        current_price.append(data['regularMarketPrice'])
        price_change.append(data['regularMarketChange'])
        percent_change.append(data['regularMarketChangePercent'])
    data_dict = {"symbol":symbols,
                 "name":names,
                 "current_price":current_price,
                 "price_change":price_change,
                 "percent_change":percent_change}
    return pd.DataFrame(data_dict)

def create_data():
    global data_generated
    print("Fetching Data")

    top_100 = generate_data('day_gainers')
    print("Data Generated:top100")

    most_active = generate_data('most_actives')
    print("Data Generated:most_active")

    trend = generate_data('aggressive_small_caps')
    print("Data Generated:trend")

    if not "list_type" in top_100.columns:
        top_100["list_type"] = ["TOP 100" for i in range(len(top_100['symbol'].to_list()))]
    if not "list_type" in most_active.columns:
        most_active["list_type"] = ["MOST ACTIVE" for i in range(len(most_active['symbol'].to_list()))]
    if not "list_type" in trend.columns:
        trend["list_type"] = ["TRENDING" for i in range(len(trend['symbol'].to_list()))]


    full_df_lst = [top_100,most_active,trend]
    full_df = pd.concat(full_df_lst)
    full_df.to_csv("data.csv",index=False)
    data_generated = True
    print("Data Generated and Saved.")

def search_start():
    d = get_chart_data("NVDA")
    cache.set('data_dict',d,timeout=60*60*24)
    print("data set in cache")

def home(request):
    global filter_applied, filter_cat, list_cat,data_generated,cat_map
    threading.Thread(target=search_start).start()
    if not os.path.exists('data.csv'):
        data_generated = False
        threading.Thread(target=create_data).start()
    else:
        data_generated = True

    if request.user.is_authenticated:
        request.session['test_cache'] = "string"
        if not data_generated:
            context = {
                "filter_applied": filter_applied,
                "filter": filter_cat,
                "list": list_cat,
                "data_availabe":data_generated,
            }
        else:
            print("data exists")
            print(data_generated)
            df = pd.read_csv("data.csv")
            df = df.loc[df['list_type'] == cat_map[list_cat]]
            table_data = df.to_dict(orient='records')
            context = {
                "filter_applied": filter_applied,
                "filter": filter_cat,
                "list": list_cat,
                "data_availabe":data_generated,
                "stocks":table_data
            }
        return render(request, 'home.html', context)
    else:
        return HttpResponse("Please Login/Signup")

def search(request):
    global filter_applied, filter_cat, list_cat
    query = request.GET.get('q')
    return redirect(reverse('stocks:ticker', args=[query]))
    # if request.user.is_authenticated:
    #     if request.method == "GET":
    #         query = request.GET.get('q')
    #         print("Query on stocks:", query)
    #         context = {
    #             "filter_applied": filter_applied,
    #             "filter": filter_cat,
    #             "list": list_cat,
    #             "query": query,
    #             "data_availabe":data_generated}
    #         return render(request, 'home.html', context)
    # else:
    #     return HttpResponse("Please Login/Signup")

def filter_cat(request):
    global filter_applied, filter_cat, list_cat
    if request.method == "GET":
        if request.GET.get("sector") is not None:
            filter_cat = request.GET.get("sector")
        if request.GET.get("list") is not None:
            list_cat = request.GET.get("list")
        filter_applied = True
        print("filter applied:", filter_cat)
        print("list selected:", list_cat)

        return redirect("stocks:market")

    return redirect("stocks:market")

def stock_data(request):
    ticker = cache.get('ticker')
    if not ticker == cache.get("previous_ticker"):
        print("New Ticker Data To be Loaded")
        d = get_chart_data(ticker)
        cache.set("previous_ticker", ticker,timeout=60*60*24)
        d['Date'] = d.index
        d['Date'] = d['Date'].dt.tz_convert('Asia/Kolkata').dt.strftime('%d/%m/%Y')
        d.reset_index(drop=True,inplace=True)
        cache.set('data_dict',d,timeout=60*60*24)
        data = {
            # "price": 150.25,
            # "change_percent": 2.5,
            "labels": d['Date'].to_list(),
            "values": d['Close'].to_list()
        }
        cache.set("chart-data",data,timeout=60*60*24)
        return JsonResponse(data)
    else:
        print("Previous Data")

        return JsonResponse(cache.get("chart-data"))

def ticker(request,ticker):
    cache.set("ticker",ticker,timeout=60*60*24)
    context = {"ticker":ticker,"data":cache.get("data_dict").to_dict(orient="records")}
    return render(request, 'ticker.html',context)