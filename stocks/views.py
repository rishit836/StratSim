from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return HttpResponse("Hello "+ str(request.user))
    else:
        return HttpResponse("Please Login/Signup")
