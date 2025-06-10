from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from stocks.models import Portfolio

# Create your views here.

def PON(val):
    if val>=0:
        return "positive"
    elif val<0:
        return "negative"
    


def home(request):

    if request.user.is_authenticated:
        portfolio = Portfolio.objects.get(user=request.user)
        fund = portfolio.current_funds
        fund_change = portfolio.profit_loss_percent()
    else:
        fund = 0

    return_val = 15.2
    active_strats = 3
    return_change = -1.2
    strat_change =  .5
    context = {'fund':"{:,}".format(fund), 'return':return_val, 'active_strats':active_strats, 'rv':PON(return_change), 'sv':PON(strat_change),'fv':PON(fund_change),"fc":fund_change,"return_change":return_change, "strat_change":strat_change}

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