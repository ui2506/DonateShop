from django.urls import path

from .views import *

urlpatterns = [
    path('donators/', donators_api, name='donators_api'),
    path('donators/give_days/', donators_api_give_days, name='donators_api_give_days'),
    path('ban/', ban, name='ban'),
    path('check_ban/', check_ban, name='check_ban'),
    path('unban/', unban, name='unban'),
    path('proxy/server/<int:scpsl_id>/', proxy_server_data, name='proxy_server_data'),
]