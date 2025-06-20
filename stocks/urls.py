from django.urls import path
from . import views

app_name="stocks"

urlpatterns=[
    path('', views.home, name="market"),
    path('search',views.search,name="search"),
    path('filter', views.filter_cat,name="filter"),
    path('ticker/<str:ticker>',views.ticker, name="ticker"),
    path('stock-data/', views.stock_data, name='stock-data'),
    path('load', views.load, name="load"),
    path('analyze/<str:ticker>',views.analyze,name="analyze")
]