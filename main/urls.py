from django.urls import path

from .views import *

urlpatterns = [
    path('', home, name="home"),
    path('login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('profile/', profile, name='profile'),
    path('servers/', server_list, name='server_list'),

    path('rules/', rules, name="rules"),
    path('rules/type/<str:type>/', rule_type, name="rule_type"),
    path('rules/game/<str:server_id>/', game_rules, name="server_rules"),
    path('rules/donate/<str:server_id>/', donate_rules, name="donate_rules"),
]