from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.models import User
from django.db.models import Q
import pandas as pd
import yfinance as yf
import os
import threading

# Global flags
filter_applied = False
list_cat = "top"
filter_cat = None

def get_data():
    # List of selected symbols to fetch
    symbols = [
        "AAPL", "MSFT", "AMZN", "GOOGL", "TSLA", "JPM", "XOM", "UNH", "V", "NVDA",
        "CVX", "PFE", "BAC", "WFC", "META", "T", "INTC", "HD", "C", "KO"
    ]

    # Allowed categories and mapping
    ALLOWED_CATEGORIES = ['technology', 'energy', 'healthcare', 'real estate', 'financial services']
    CATEGORY_MAP = {
        'technology': 'tech',
        'energy': 'energy',
        'healthcare': 'healthcare',
        'real estate': 'real estate',
        'financial services': 'finance',
    }

    final_data = []
    print("Fetching data from Yahoo Finance...")

    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            name = info.get("longName") or info.get("shortName") or "N/A"
            price = info.get("currentPrice")
            previous_close = info.get("previousClose")
            change = round((price - previous_close), 2) if price and previous_close else None
            sector = info.get("sector", "").lower()

            category = CATEGORY_MAP.get(sector)
            if category:
                final_data.append({
                    "symbol": symbol,
                    "name": name,
                    "price": price,
                    "change": change,
                    "category": category,
                    "list_type": "top100"  # You can modify this dynamically
                })

        except Exception as e:
            print(f"Failed to fetch {symbol}: {e}")
            continue

    df = pd.DataFrame(final_data)
    df.to_csv('data.csv', index=False)
    print("Data saved to data.csv")
def start_data_fetch():
    thread = threading.Thread(target=get_data)
    thread.daemon = True
    thread.start()
def home(request):
    global filter_applied, filter_cat, list_cat
    df = None
    table_data = None
    columns = []
    if not os.path.exists("data.csv"):
        start_data_fetch()
    if os.path.exists("data.csv"):
        df = pd.read_csv("data.csv")
        if not df.empty:
            table_data = df.to_dict(orient='records')
            columns = list(df.columns)
    if request.user.is_authenticated:
        context = {
            "filter_applied": filter_applied,
            "filter": filter_cat,
            "list": list_cat,
            "table_data": table_data,
            "columns": columns
        }
        return render(request, 'home.html', context)
    else:
        return HttpResponse("Please Login/Signup")

def search(request):
    global filter_applied, filter_cat, list_cat
    if request.user.is_authenticated:
        if request.method == "GET":
            query = request.GET.get('q')
            print("Query on stocks:", query)
            context = {
                "filter_applied": filter_applied,
                "filter": filter_cat,
                "list": list_cat,
                "query": query
            }
            return render(request, 'home.html', context)
    else:
        return HttpResponse("Please Login/Signup")

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
