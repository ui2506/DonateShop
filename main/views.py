from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages, auth
from django.utils import timezone
from django.db.models import Q
from django.utils.timezone import now
from django.http import Http404
from donate.models import Donate, Purchase, Transaction, Present
from DonateShop.utils import get_client_ip

from .models import *

def home(request):
    rich_users = Player.objects.filter(is_hidden=False).order_by('-max_money')[:7]    

    donates = list(Donate.objects.filter(is_buyable=True).order_by('-count')[:3])

    top_players = PlayerXP.objects.using('scpsl').order_by('-lvl').values('nickname', 'lvl')[:10]
    top_time = PlayerXP.objects.using('scpsl').order_by('-total_seconds').values('nickname', 'total_seconds')[:10]

    if len(donates) >= 2:
        donates[0], donates[1] = donates[1], donates[0]

    return render(request, 'home.html', {
        'user': request.user,
        'url': request.resolver_match.url_name,
        'rich_users': rich_users,
        'donates': donates,
        'top_players': top_players,
        'top_time': top_time
    })

def login(request):
    if request.user.is_authenticated:
        messages.warning(request, "Вы уже зарегестрированы! Зачем опять регистрироваться? :/")
        return redirect("home")
        
    return render(request, 'login.html')

def logout(request):
    auth.logout(request)
    return redirect('home')

def profile(request):
    user = request.user

    if not user.is_authenticated:
        return redirect("login")
    
    ip = get_client_ip(request)

    purchases = Purchase.objects.filter(player=user, is_hidden=False).all()
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')[:10]
    presents = Present.objects.filter(recipient=user, is_used=False).all()
    punishments = PlayerPunishment.objects.using('scpsl').filter(Q(target_id=f"{user.user_id}@steam") | Q(target_id=ip)).order_by('-created_at')[:10]

    if not user.last_update or now() - user.last_update > timedelta(days=1):
        user.update()
        
    if request.method == "POST":
        deactivate_donate_id = request.POST.get("deactivate_donate_id")
        hide_donate_id = request.POST.get("hide_donate_id")
        hide_me = request.POST.get("hide_me")

        accept_present_id = request.POST.get('accept_present_id')
        cancel_present_id = request.POST.get('cancel_present_id')

        if deactivate_donate_id:
            donate = get_object_or_404(Purchase, id=deactivate_donate_id, player=user)
            donate.is_disabled = True
            donate.save()

            messages.success(request, "Донат деактивирован... :(")

            return redirect("profile")
        elif hide_donate_id:
            donate = get_object_or_404(Purchase, id=hide_donate_id, player=request.user)
            donate.is_hidden = True
            donate.save()

            messages.success(request, "Донат удален... :(")

            return redirect("profile")
        elif hide_me:
            if user.is_hidden:
                user.is_hidden = False
                messages.success(request, "Ваш аккаун снова может показаться в топе донатеров!")
            else:
                user.is_hidden = True
                messages.success(request, "Ваш аккаун скрыт с топа донатеров!")
            
            user.save()

            return redirect("profile")
        elif cancel_present_id:
            # present = get_object_or_404(Present, recipient=user, id=accept_present_id)
            
            # messages.warning(request, f"Вы отказались от подарка от {present.donor.nickname} 😞")
            messages.error(request, "В данный момент не доступно")
            return redirect("profile")
        elif accept_present_id:
            present = get_object_or_404(Present, recipient=user, id=accept_present_id)

            purchase = purchases.filter(donate=present.donate, is_disabled=False, expires_at__gt=timezone.now())

            if purchase:
                messages.error(request, f"У вас уже есть схожи донат. Дождитесь конца старого доната!")
                return redirect("profile")

            present.use()

            messages.success(request, f"Вы приняли подарок от {present.donor.nickname}❤️")
            return redirect("profile")

    return render(request, 'profile.html', {
        'url': request.resolver_match.url_name, 
        'donates': purchases, 
        'transactions': transactions,
        'presents': presents,
        'punishments': punishments
        })

def unban(request, id):
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, 'С начало войди в аккаунт ^^')
        return redirect('login')

    punishments = PlayerPunishment.objects.using('scpsl').get(id=id)

    if not punishments:
        messages.error(request, 'Блокировка не найдена!')
        return redirect('profile')
    
    if punishments.target_id != f"{user.user_id}@steam" and punishments.target_id != get_client_ip(request):
        messages.warning(request, f'Хммм, мне кажется это не твой бан.')
        return redirect('profile')
    
    if not punishments.is_active() or punishments.is_revoked:
        messages.warning(request, 'Уже можно не платить. Срок наказания истек, или блокировка снята')
        return redirect('profile')
    
    price = punishments.price()

    if user.balance < price:
        messages.warning(request, 'У вас немного не хватает деняг... :3')
        return redirect('balance')
    
    punishments.is_revoked = True
    punishments.save()

    PunishmentHistory.objects.using('scpsl').create(punishment_id=punishments.id, action="revoked", issuer_id="Web site", reason="Покупка снятие ограничений")

    user.balance -= price
    user.save()

    Transaction.objects.create(user=user, amount=price, type="charge", reason=f"Покупка разбана. Ban id: {id}")

    messages.success(request, 'Вы успешно купили разбан!')
    return redirect('profile')

def server_list(request):
    servers = Server.objects.all()

    return render(request, 'server_list.html', {
        'servers': servers
        })

def rules(request):
    rules = Rule.objects.all()
    return render(request, 'rules/main.html', {
        'rules': rules
        })

def rule_type(request, type):
    match type:
        case 'offer':
            return render(request, 'rules/policy/offer.html')
        case 'privacy':
            return render(request, 'rules/policy/privacy.html')
        case 'admin':
            return render(request, 'rules/other/admin.html')

    return render(request, '404.html')

def donate_rules(request, server_id):
    if not server_id.isdigit():
        raise Http404("Server not found")

    server = get_object_or_404(Server, server_id=server_id)
    rules = get_object_or_404(Rule, server=server)

    return render(request, 'rules/rule.html', {
        'rules': rules.donate_rules, 
        'title': 'Правила донатов'
        })

def game_rules(request, server_id):
    if not server_id.isdigit():
        raise Http404("Server not found")
        
    server = get_object_or_404(Server, server_id=server_id)
    rules = get_object_or_404(Rule, server=server)
    
    return render(request, 'rules/rule.html', {
        'rules': rules.game_rules, 
        'title': 'Правила сервера'
        })