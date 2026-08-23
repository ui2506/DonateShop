from django.contrib import admin
from .models import *

admin.site.register([Player, Server, Rule, GameRule, DonateRule])
