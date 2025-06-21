from django.shortcuts import render,HttpResponse

# Create your views here.

def predict(request,ticker):
    return HttpResponse("data proccessing started for ticker :" + str(ticker))
    



def home(request):
    return HttpResponse("Hello!, This is a breakdown app")


