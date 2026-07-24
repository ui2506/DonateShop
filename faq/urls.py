from django.urls import path
from .views import *

urlpatterns = [
    path("", faq, name="faq"),
    path("<str:name>/", show_faq, name="show_faq")
]