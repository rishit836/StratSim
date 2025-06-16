from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from stocks.models import Portfolio,Strategy,holding
from django.db.models import Q

# Create your views here.

def PON(val):
    if val>0 or val == 0:
        return "positive"
    elif val<0:
        return "negative"
    

def home(request):
    if request.method == "GET":
        query = request.GET.get('q')
        # print("Query!!", query)

    if request.user.is_authenticated:
        portfolio = Portfolio.objects.get(user=request.user)
        fund = portfolio.total_value()
        fund_change = portfolio.profit_loss_percent()
        return_change = portfolio.update_return_history()
        strategies = Strategy.objects.filter(user=request.user, is_active=True)
        current_return = portfolio.profit_loss_percent()
        invested_funds = 0
        holdings = holding.objects.filter(user=request.user)

        for h in holdings:
            invested_funds += h.quantity * h.current_price
    else:
        fund = 0
        portfolio = 0
        fund = 0
        fund_change = 0
        return_change = 0
        strategies = 0
        current_return = 0

    return_val = current_return
    if strategies:
        active_strats = strategies
    else:
        active_strats = 0
        strat_change =  0

    
    context = {'fund':"{:,}".format(fund), 'return':return_val, 'active_strats':active_strats, 'rv':PON(return_change), 'sv':PON(strat_change),'fv':PON(fund_change),"fc":fund_change,"return_change":return_change, "strat_change":strat_change,"invested_funds":invested_funds}

    return render(request,'index.html',context)

def market(request):
    return render(request, 'market.html')


def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username,password=password)
        if user is not None:
            login(request,user)
            messages.success(request, "you have succesfully logged in.")
            return redirect('main:home')
        else:
            messages.error(request, "Invalid Username or password")
    return render(request,'login.html', {"message":True})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST['email']
        u = User.objects.create_user(username=username, email=email, password=password)
        u.save()
        messages.success(request, "You have Succesfully signed up and logged in.")
        login(request,u)
        return redirect('main:home')
    return render(request, 'signup.html')

def logout_view(request):
    logout(request)
    for message  in list(messages.get_messages(request)):
        del message
    return redirect('main:home')

def account(request):
    return render(request, 'account.html')