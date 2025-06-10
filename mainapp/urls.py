from django.urls import path
from . import views
app_name='main'
urlpatterns = [
    path('',views.home, name='home'),
    path('market', views.market, name="market"),
    path('signup', views.signup, name="signup"),
    path('account',views.account,name="account"),
    path('logout',views.logout_view,name="logout"),
    path('login', views.login_view, name="login")
]
