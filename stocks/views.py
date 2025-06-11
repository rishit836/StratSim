from django.shortcuts import render,HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
# Create your views here.

def home(request):
    if request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return HttpResponse("Please Login/Signup")
def search(request):
    if request.user.is_authenticated:
        if request.method == "GET":
            query = request.GET.get('q')
            print("Query on stocks:", query)
            context={"query":query}
        return render(request, 'home.html',context)
    else:
        return HttpResponse("Please Login/Signup")