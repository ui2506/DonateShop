from django.urls import path

from .views import *

urlpatterns = [
    path('donators/', donators_api, name='donators_api'),
    path('donators/give_days/', donators_api_give_days, name='donators_api_give_days'),
]