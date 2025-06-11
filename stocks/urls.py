from django.urls import path
from . import views

app_name="stocks"

urlpatterns=[
    path('', views.home, name="market"),
    path('search',views.search,name="search")
]