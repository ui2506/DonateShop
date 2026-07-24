from django.urls import path
from .views import *

urlpatterns = [
    path('user_list/', user_list, name='admin_user_list'),
    path('transactions/', transactions, name='admin_transactions'),
    path('user_profile/<str:user_id>/', user_profile, name='admin_user_profile'),
    path('give_present/', give_present, name='give_present')
]