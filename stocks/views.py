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
from .operations import delete_if_outdated,create_sector
from .trade import execute_trade
from .models import holding
from walletTree import modelling
from django.contrib import messages

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
finnhub_to_button_category = {
    # --- Technology ---
    "Technology": "technology",
    "Semiconductors": "technology",
    "Software & Services": "technology",
    "Technology Hardware & Equipment": "technology",
    "IT Services": "technology",
    "Internet Services & Infrastructure": "technology",
    "Telecommunication": "technology",
    "Media": "technology",  # Often digital media, fits better in tech for most firms
    "Life Sciences Tools & Services": "technology",  # Often biotech-tech hybrid
    "Professional Services": "technology",  # Assume tech consulting unless domain-specific
    "Commercial Services & Supplies": "technology",  # Can include IT logistics
    "Diversified Consumer Services": "technology",  # e.g. EdTech, SaaS platforms

    # --- Energy ---
    "Energy": "energy",
    "Oil, Gas & Consumable Fuels": "energy",
    "Oil & Gas Equipment & Services": "energy",
    "Renewable Electricity": "energy",
    "Independent Power Producers & Energy Traders": "energy",
    "Utilities": "energy",

    # --- Healthcare ---
    "Health Care": "healthcare",
    "Pharmaceuticals": "healthcare",
    "Life Sciences Tools & Services": "healthcare",
    "Health Care Providers & Services": "healthcare",
    "Health Care Equipment & Services": "healthcare",

    # --- Real Estate ---
    "Real Estate": "estate",
    "Equity Real Estate Investment Trusts (REITs)": "estate",
    "Real Estate Management & Development": "estate",

    # --- Finance ---
    "Financials": "finance",
    "Banking": "finance",
    "Banks": "finance",
    "Capital Markets": "finance",
    "Insurance": "finance",
    "Consumer Finance": "finance",
    "Diversified Financials": "finance",
    "Financial Services": "finance",

    # ------- Other mappings (use best-fit strategy) -------
    "Electrical Equipment": "technology",  # Often overlaps with electronics and power-tech
    "Auto Components": "technology",  # Includes sensors, chips, automation
    "Automobiles": "technology",  # EV and connected cars have tech base
    "Aerospace & Defense": "technology",  # Usually includes avionics, defense tech
    "Airlines": "technology",  # Often includes logistics/air-tech, can also be "other"
    "Metals & Mining": "energy",  # Needed for batteries, oil, etc.
    "Consumer products": "healthcare",  # Most often pharma, wellness, etc.
    "Food Products": "healthcare",  # Food tech / nutrition focus

    # N/A or unknown fallback
    "N/A": "None"
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
        names.append(data['shortName'])
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
    global data_generated,finnhub_to_button_category
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
    
    print("Data Generated and Saved.Now Creating Sectors...")
    sectors = create_sector()
    sec_column = []
    for num,row in full_df.iterrows():
        if row['symbol'] in sectors.keys():
            sec_column.append(sectors[row['symbol']])
        else:
            sec_column.append("None")
    full_df['sectors'] = sec_column
    secs = []
    values_not_seg = []
    for num,row in full_df.iterrows():
        if row['sectors'] in finnhub_to_button_category.keys():
            secs.append(finnhub_to_button_category[row['sectors']])
            row['sectors'] = finnhub_to_button_category[row['sectors']]
        else:
            values_not_seg.append(row['sectors'])
            secs.append(row['sectors'])
    full_df['sectors'] = secs
    print('/n'*5)
    print(values_not_seg)
    full_df.to_csv("data.csv",index=False)
    data_generated = True




def home(request):
    global filter_applied, filter_cat, list_cat,data_generated,cat_map
    delete_if_outdated('data.csv')
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
        messages.error(request,"please login,market cannot be accesed without login")
        return redirect("main:login")

def search(request):
    global filter_applied, filter_cat, list_cat
    query = request.GET.get('q')
    return redirect(reverse('stocks:ticker', args=[query]))

def filter_cat(request):
    global filter_applied, filter_cat, list_cat
    if request.method == "GET":
        if request.GET.get("sector") is not None:
            filter_cat = request.GET.get("sector")
            if filter_cat != "clear":

                filter_applied = True
            else:
                # remove the filter
                filter_applied = False
        if request.GET.get("list") is not None:
            list_cat = request.GET.get("list")
        
        print("filter applied:", filter_cat)
        print("list selected:", list_cat)

        return redirect("stocks:market")

    return redirect("stocks:market")

def stock_data(request):
    return JsonResponse(cache.get("chart-data"))


def update_holdings(request,ticker):
    print("checking")
    holdings = holding.objects.filter(user = request.user)
    if holdings.exists():
        for h in holdings:
            print(h.ticker)
            if h.ticker.lower() == ticker.lower():
                print("owned")
                cache.set("data_available",True)
                cache.set("share_quantity", h.quantity)
                cache.set("ticker", h.ticker)
                cache.set("price", h.current_price)
    else:
        print("not owned")
        cache.set("data_available",False)
        
        
        
        


def ticker(request,ticker):
    global data_loaded
    update_holdings(request,ticker)

    if cache.get("previous_ticker") != ticker:
        data_loaded = False

        cache.set("ticker", ticker,timeout=60*60*24)
        return redirect('stocks:load')
    else:
        try: 
            if request.session["buy-mode"]:
                pass
        except:
            request.session["buy-mode"]="buy"
        if request.method == "GET":
            if request.GET.get("modebutton") is not None:
                request.session['buy-mode'] = request.GET.get("modebutton")
            if request.GET.get("quantity") is not None:
                request.session['quantity'] = request.GET.get("quantity")
            if request.GET.get("execute") is not None:
                ticker_symbol = cache.get('ticker')
                quantity = request.session['quantity']
                action = request.session['buy-mode']
                state,message = execute_trade(request, request.user, ticker_symbol, action, quantity)
                update_holdings(request,ticker)
                context = {"ticker":ticker,"data":cache.get("data_dict").to_dict(orient="records"),"mode":request.session['buy-mode'],"message":message,"state":state,"data_available":cache.get('data_available'),"share_quantity":cache.get("share_quantity"),
            "ticker":cache.get("ticker"),
            "price":cache.get("price")}
                

                return render(request,'ticker.html',context=context)
                


        if request.session['buy-mode'] is not None:
            context = {"ticker":ticker,"data":cache.get("data_dict").to_dict(orient="records"),"mode":request.session['buy-mode'],"data_available":cache.get('data_available'),"share_quantity":cache.get("share_quantity"),
            "ticker":cache.get("ticker"),
            "price":cache.get("price")}
        else:
           
            context = {"ticker":ticker,"data":cache.get("data_dict").to_dict(orient="records"),"mode":'buy',"data_available":cache.get('data_available'),"share_quantity":cache.get("share_quantity"),
            "ticker":cache.get("ticker"),
            "price":cache.get("price")}
        return render(request, 'ticker.html',context)


def background_loader():
    try:
        global data_loaded,loading_data,error_occured

        t = cache.get("ticker")
        print("loading data for",t)

        cache.set("previous_ticker",t,timeout=60*60*24)
        ticker = yf.Ticker(t)
        d = ticker.history(period='1mo')
        d['Date'] = d.index
        d['Date'] = d['Date'].dt.tz_convert('Asia/Kolkata').dt.strftime('%d/%m/%Y')
        d.reset_index(drop=True,inplace=True)
        cache.set('data_dict',d,timeout=60*60*24)
        data = {
                "labels": d['Date'].to_list(),
                "values": d['Close'].to_list()
            }
        cache.set("chart-data",data,timeout=60*60*24)
        cache.set("data_available", False)
        holdings = holding.objects.filter(user = r_l.user)
        for h in holdings:
            if h.ticker.lower() == cache.get("ticker").lower():
                print("user owns", cache.get("ticker"))
                cache.set("data_available",True)
                cache.set("share_quantity", h.quantity)
                cache.set("ticker", h.ticker)
                cache.set("price", h.current_price)
        data_loaded = True
        loading_data=False
        error_occured = False
        print("chart should be visible")
    except:
        data_loaded = False
        loading_data = False
        error_occured = True
        print("Some Unknown Error Occured.Error From Yfinance api.")




            


loading_data = False
error_occured = False
def load(request):
    global loading_data,r_l,error_occured
    r_l = request
    if not loading_data and not error_occured:
        threading.Thread(target=background_loader).start()
        loading_data = True
    if error_occured:
        messages.error(request,"Yfinance Couldnt Return the data for the requested ticker.")
        error_occured = False
        return redirect(reverse("stocks:market"))
    if not data_loaded:
        return render(request, 'loader.html')
    else:
        return redirect(reverse('stocks:ticker', args=[cache.get("ticker")] ))
    


def analyze(request,ticker):
    print("ticker analysis started for ticker:", ticker)
    c = {"ticker":ticker}
    if request.method == "POST":
        chart_view = request.POST.get("chart-view")
        print(chart_view)
    # return render(request,"analyze.html",c)
    return redirect(reverse("wallettree:scrape",args=[ticker]))