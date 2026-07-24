from django.urls import path

from .views import *

urlpatterns = [
    path('balance/', balance, name="balance"),
    # path('balance/replenish/', replenish_balance, name="replenish_balance"),
    path("balance/payment/create/", create_payment_v2, name="create_payment"),
    
    path('seller/', seller, name='seller'),

    # path("payment/create/<str:payment>/<int:amount>/", create_payment, name="create_payment"),
    path("payment/webhook/antilopay/", antilopay_payment_webhook, name="antilopay_payment_webhook"),
    path('payment/success/', payment_success, name="payment_success"),
    path('payment/fail/', payment_fail, name="payment_fail"),

    path('', shop_server_list, name="shop_server_list"),
    path('<str:server_id>/', shop_donate_list, name="shop_donate_list"),
    path('<str:server_id>/<str:donate_name>/', buy_by_id, name="buy_by_id"),
    path('<str:server_id>/<str:donate_name>/gift/', gift_by_id, name="gift_by_id"),
]