from django.shortcuts import render, redirect, get_object_or_404
from .models import Player, Donate, Purchase, Server, Payment, Transaction, Present
from django.contrib import messages
from django.http import JsonResponse, Http404
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.utils.http import url_has_allowed_host_and_scheme
from django_ratelimit.decorators import ratelimit
from django.urls import reverse
from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from urllib.parse import urlencode

import json
import time
import requests
import DonateShop.settings as settings
import base64

from Cryptodome.Signature import pkcs1_15
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA

PAYMENT_METHODS = {
    "ru_card": "antilopay",
    "sbp": "antilopay",
    "world_card": "seller",
    "kz_card": "seller",
}

@login_required
@require_POST
@ratelimit(key='ip', rate='1/s', block=True)
def create_payment_v2(request):
    raw_amount = request.POST.get("amount", "").strip()
    payment_method = request.POST.get("payment_method", "").strip()
    redirect_to = request.POST.get("redirect_to", settings.ANTILOPAY_SUCCESS_URL).strip()
    email = request.POST.get("email", "server@praniksl.com").strip()

    provider = PAYMENT_METHODS.get(payment_method)

    if provider is None:
        messages.error(request, "Выбран неизвестный способ оплаты.")
        return redirect("balance")
    
    if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
        redirect_to = settings.ANTILOPAY_SUCCESS_URL

    try:
        amount = Decimal(raw_amount)
    except (InvalidOperation, TypeError):
        messages.error(request, "Введите корректную сумму.")
        return redirect("balance")

    if amount != amount.to_integral_value():
        messages.error(request, "Сумма должна быть целым числом.")
        return redirect("balance")

    if amount < 10:
        messages.error(request, "Минимальная сумма пополнения — 10 ₽.")
        return redirect("balance")

    if amount > 10_000:
        messages.error(request, "Максимальная сумма одного пополнения — 10 000 ₽.")
        return redirect("balance")

    amount = int(amount)
    order_id = f"{request.user.user_id}_{int(time.time())}"

    if provider == "antilopay":
        private_key = f"{settings.ANTILOPAY_SECRET_KEY}"

        data = {
            "project_identificator": settings.ANTILOPAY_PROJECT_ID,
            "amount": amount,
            "order_id": order_id,
            "currency": "RUB",
            "product_name": "Пополнение баланса",
            "product_type": "services",
            "description": f"Пополнение личного баланса игрока {request.user.nickname}",
            "customer": {"email": email},
            "success_url": redirect_to
        }

        print(data)

        str_payload = json.dumps(data, indent=4)
        rsa_key = RSA.importKey(base64.b64decode(private_key))
        payload = bytes(str_payload, 'UTF-8')
        hash = SHA256.new(payload)
        sign = base64.b64encode(pkcs1_15.new(rsa_key).sign(hash))
        url = "https://lk.antilopay.com/api/v1/payment/create"

        headers = {
            "Content-Type": "application/json",
            "X-Apay-Secret-Id": settings.ANTILOPAY_SECRET_ID,
            "X-Apay-Sign": sign
        }

        response = requests.post(url, data=payload, headers=headers)

        payment_data = response.json()

        if "payment_url" in payment_data:
            print("💳 Успех! Перенаправление на оплату:", payment_data["payment_url"])
            Payment.objects.create(user=request.user, amount=amount, status="pending", order_id=order_id)
            return redirect(payment_data["payment_url"])
        else:
            raise Exception(f"❌ Ошибка платежа: {payment_data}")
        
    if provider == "seller":
        return redirect("seller")

    messages.error(request, "Не удалось определить платёжную систему.")
    return redirect("balance")

@csrf_exempt
def antilopay_payment_webhook(request):
    print(f"Обрабатывает WebHook от antilopay {request.method}")

    if request.method != "POST":
        return JsonResponse({"error": "Метод не разрешен"}, status=405)

    try:
        data = json.loads(request.body)

        print(data)

        webhook_type  = data.get("type")
        status = data.get("status")

        match (webhook_type):
            case 'refund':
                if status != "COMPLETE":
                    return JsonResponse({"error": "Status must be COMPLETE"}, status=200)

                amount = data.get("amount")
                amount = int(amount)

                payment_id = data.get("payment_id")

                try:
                    payment = Payment.objects.get(system_id=payment_id)
                except Payment.DoesNotExist:
                    return JsonResponse({"error": "Payment not found"}, status=404)
                
                if amount != payment.amount:
                    return JsonResponse({"error": "Amount mismatch"}, status=400)
                
                if payment.status == "refund":
                    return JsonResponse({"status": "already_processed"}, status=200)
                
                if payment.status != "success":
                    return JsonResponse({"error": "Payment cannot be refunded"}, status=200)
                
                user = payment.user
                user.balance -= amount
                user.max_money -= amount
                user.save()

                payment.status = "refund"
                payment.save()

                Transaction.objects.create(user=user, amount=amount, type="charge", reason="Возврат средств с AntiloPay")

                return JsonResponse({"status": "success"}, status=200)
            
            case 'payment':
                if status != "SUCCESS":
                    return JsonResponse({"error": "Status must be success"}, status=200)
        
                order_id = data.get("order_id")

                try:
                    payment = Payment.objects.get(order_id=order_id)
                except Payment.DoesNotExist:
                    return JsonResponse({"error": "Payment not found"}, status=404)

                amount = data.get("original_amount")
                amount = int(amount)

                if amount != payment.amount:
                    return JsonResponse({"error": "Amount mismatch"}, status=400)

                if payment.status == "success":
                    return JsonResponse({"status": "already_processed"}, status=200)

                if payment.status != "pending":
                    return JsonResponse({"error": "Invalid payment status"}, status=200)
                
                payment_id = data.get("payment_id")
                
                payment.status = "success"
                payment.system_id = payment_id
                payment.save()

                user = payment.user
                user.max_money += amount
                user.balance += amount
                user.save()

                Transaction.objects.create(user=user, amount=amount, type="replenishment", reason="Пополнение с AntiloPay")

                print("Операция завершена!")

                return JsonResponse({"status": "success"}, status=200)
            
        return JsonResponse({"error": "Ошибка валидации данных"}, status=422)
    except (json.JSONDecodeError, TypeError, ValueError):
        return JsonResponse({"error": "Ошибка валидации данных"}, status=422)

def seller(request):
    return render(request, 'seller.html')

def shop_server_list(request):
    servers = Server.objects.all()
    return render(request, 'shop/server_list.html', {'user': request.user, 'url': request.resolver_match.url_name, 'servers': servers})

def shop_donate_list(request, server_id):
    if not server_id.isdigit():
        raise Http404("Server not found")
    
    if request.method == "POST":
        user = request.user

        if not user.is_authenticated:
            messages.error(request, "Мы, если что, не всевидящие. Зарегистрируйся, чтобы мы могли понять, кому выдать донат :3")
            return redirect("shop_donate_list", server_id=server_id)

        action: str = request.POST.get("action")

        if action == "delete":
            if not user.prefix:
                messages.error(request, "У вас нет префикса для удаления!")
                return redirect("shop_donate_list", server_id=server_id)
            
            user.prefix = ''
            user.save()

            messages.success(request, "Вы успешно удалил префикс!")
            return redirect("shop_donate_list", server_id=server_id)
            
        else:
            prefix: str = request.POST.get("prefix")

            if user.balance < 149:
                messages.error(request, "Не достаточно средств!")
                amount = int(149 - user.balance)
                query = urlencode({
                    "amount": amount,
                    "redirect_to": request.build_absolute_uri(),
                })
                return redirect(f"{reverse('balance')}?{query}")

            if not prefix:
                messages.error(request, "Префикс не может быть пустым!")
                return redirect("shop_donate_list", server_id=server_id)
            
            user.prefix = prefix
            user.balance -= 149
            user.save()

            Transaction.objects.create(user=user, amount=149, type="charge", reason=f'Покупка доната префикса для сервера \"{server_id}\"')

            messages.success(request, "Вы успешно изменили префикс!")
            return redirect("shop_donate_list", server_id=server_id)

    server = get_object_or_404(Server, server_id=server_id)
    donates = Donate.objects.filter(server=server).all()

    return render(request, 'shop/donate_list.html', {'user': request.user, 'url': request.resolver_match.url_name, 'donates': donates, 'server_id': server.server_id})

def buy_by_id(request, server_id, donate_name):
    user = request.user

    if not user.is_authenticated:
        messages.error(request, "Мы, если что, не всевидящие. Зарегистрируйся, чтобы мы могли понять, кому выдать донат :3")
        return redirect("login")

    if not server_id.isdigit():
        raise Http404("Server not found")

    server = get_object_or_404(Server, server_id=server_id)  
    donate = get_object_or_404(Donate, name=donate_name, server=server)

    if donate.is_buyable == False:
        messages.error(request, "Этот донат возможно купить только через Discord!")
        return redirect("shop_donate_list", server_id=server_id)

    days = request.GET.get("days")

    if days and days.isdigit():
        days = str(int(days))
    else:
        messages.error(request, "Пытаешься сломать систему? XD")
        return redirect("shop_donate_list", server_id=server_id)

    if days not in donate.price:
        messages.error(request, "Пытаешься сломать систему? XD")
        return redirect("shop_donate_list", server_id=server_id)

    price = donate.price[days]

    if request.method == "POST":
        purchase = Purchase.objects.filter(player=user, expires_at__gt=now(), is_disabled=False, server=server).exclude(donate=donate).first()

        if purchase:
            messages.error(request, "Вы уже приобрели донат на этот сервер! Диактевируйте старый донат, что бы купить новый!")
            return redirect("shop_donate_list", server_id=server_id)

        if user.balance < price:
            messages.error(request, "Недостаточно средств. Пожалуйста пополните баланс.")
            amount = int(price - user.balance)
            query = urlencode({
                "amount": amount,
                "redirect_to": request.build_absolute_uri(),
            })
            return redirect(f"{reverse('balance')}?{query}")
        
        purchase = Purchase.objects.filter(player=user, expires_at__gt=now(), is_disabled=False, server=server, donate=donate).first()

        user.balance -= price
        user.save()
        Transaction.objects.create(user=user, amount=price, type="charge", reason=f'Покупка доната {donate.title} на {days} дней для сервера \"{donate.server.name}\"')

        if purchase:
            purchase.expires_at += timedelta(days=int(days))
            purchase.save()
            messages.success(request, f"Вы успешно продлили {donate.title} на {days} дней! Спасибо за покупку :3")
        else:
            purchase = Purchase.objects.filter(player=user, is_disabled=False, server=server, donate=donate).first()

            if purchase:
                purchase.expires_at = now() + timedelta(days=int(days))
                purchase.save()
                messages.success(request, f"Вы успешно продлили {donate.title} на {days} дней! Спасибо за покупку :3")
            else:
                Purchase.objects.create(player=user, donate=donate, server=server, expires_at=now() + timedelta(days=int(days)))
                donate.update_count()
                messages.success(request, f"Вы успешно приобрели {donate.title} на {days} дней! Спасибо за покупку :3")

        return redirect("profile")

    return render(request, 'shop/buy.html', {'user': user, 'donate': donate, 'price': price, 'days': days})

def gift_by_id(request, server_id, donate_name):
    if not server_id.isdigit():
        raise Http404("Server not found")
    
    server = get_object_or_404(Server, server_id=server_id)  
    donate = get_object_or_404(Donate, name=donate_name, server=server)

    user = request.user

    if not user.is_superuser and not donate.is_buyable:
        messages.error(request, "Этот донат возможно купить только через Discord!")
        return redirect("shop_donate_list", server_id=server_id)

    days = request.GET.get("days")

    if days and days.isdigit():
        days = str(int(days))
    else:
        messages.error(request, "Неверное количество дней для покупки.")
        return redirect("shop_donate_list", server_id=server_id)

    if days not in donate.price:
        messages.error(request, "Пытаешься сломать систему? XD")
        return redirect("shop_donate_list", server_id=server_id)

    price = donate.price[days]

    if request.method == "POST":
        if not user.is_authenticated:
            messages.error(request, "Мы, если что, не всевидящие. Зарегистрируйся, чтобы мы могли понять, какой у тебя баланс :3")
            return redirect("login")
        
        target_id = request.POST.get("steam_id")

        if not target_id:
            messages.error(request, "Вы не ввели Steam")
            return redirect("shop_donate_list", server_id=server_id)
        
        target = Player.objects.filter(user_id=target_id).first()

        if not target:
            messages.error(request, "Игрок не зарегестрирован на сайте!")
            return redirect("shop_donate_list", server_id=server_id)
        
        comment = request.POST.get('comment')

        if not comment:
            messages.error(request, "Вы не ввели комментарий")
            return redirect("shop_donate_list", server_id=server_id)

        if user.balance < price:
            messages.error(request, "Недостаточно средств. Пожалуйста пополните баланс.")
            amount = int(price - user.balance)
            query = urlencode({
                "amount": amount,
                "redirect_to": request.build_absolute_uri(),
            })
            return redirect(f"{reverse('balance')}?{query}")

        Present.objects.create(donor=user, recipient=target, donate=donate, days=days, comment=comment)
        donate.update_count()

        if user.balance >= price:
            user.balance -= price
            user.save()
            Transaction.objects.create(user=user, amount=price, type="charge", reason=f'Покупка подарка {donate.title} на {days} дней для сервера \"{donate.server.name}\"')

        messages.success(request, f"Вы успешно купили донат игроку {target.nickname}.")
        return redirect("home")

    return render(request, 'shop/gift.html', {'user': user, 'donate': donate, 'price': price, 'days': days})

def replenish_balance(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        amount = request.POST.get('amount')

        if int(amount) < 10:
            messages.error(request, 'Минимальная сумма 10 рублей')
            return redirect('balance')

        return render(request, 'balance/replenish.html', {
            'amount': amount
            })
    
    messages.error(request, 'Ошибка обработки запроса.')
    return redirect('home')

def balance(request):
    user = request.user

    if not user.is_authenticated:
        return redirect('login')

    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    return render(request, 'balance/balance.html', {
        'transactions': transactions
    })

def payment_success(request):
    return render(request, 'payments/success.html')

def payment_fail(request):
    return render(request, 'payments/failed.html')