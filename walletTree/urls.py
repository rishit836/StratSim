from django.urls import path
from . import views

app_name="wallettree"

urlpatterns = [
    path("", views.home, name="home"),
    path("/predict/<str:ticker>", views.predict, name="predict")
]