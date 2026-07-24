from django.contrib import admin

import donate.models as data

admin.site.register([data.Purchase, data.Payment, data.Transaction, data.Present, data.Donate])