from datetime import timedelta
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.utils.timezone import now
from main.models import Player
from donate.models import Transaction, Purchase, Donate, Present

def user_list(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        messages.warning(request, 'Куда лезим?)))')
        return redirect('home')
    
    players_list = Player.objects.all().order_by('-date_joined')
    paginator = Paginator(players_list, 12)

    page_number = request.GET.get('page')
    players = paginator.get_page(page_number)

    return render(request, 'user_list.html', {'players': players})

def transactions(request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        messages.warning(request, 'Куда лезим?)))')
        return redirect('home')
    
    transaction_list = Transaction.objects.order_by('-created_at').all()

    today = now().date()
    week_ago = today - timedelta(days=7)

    total_replenishment = Transaction.objects.filter(type='replenishment').aggregate(Sum('amount'))['amount__sum'] or 0

    total_month_replenishment = Transaction.objects.filter(
        type='replenishment',
        created_at__month=today.month,
        created_at__year=today.year
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_week_replenishment = Transaction.objects.filter(
        type='replenishment',
        created_at__date__gte=week_ago
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    total_day_replenishment = Transaction.objects.filter(
        type='replenishment',
        created_at__date=today
    ).aggregate(Sum('amount'))['amount__sum'] or 0

    paginator = Paginator(transaction_list, 10)
    page_number = request.GET.get('page')
    transactions = paginator.get_page(page_number)

    return render(request, 'transactions.html', {
        'transactions': transactions,
        'total_replenishment': total_replenishment,
        'total_month_replenishment': total_month_replenishment,
        'total_week_replenishment': total_week_replenishment,
        'total_day_replenishment': total_day_replenishment
    })

def user_profile(request, user_id):
    if not request.user.is_superuser:
        messages.warning(request, 'Куда лезим?)))')
        return redirect('home')
    
    player = Player.objects.filter(user_id=user_id).first()

    if not player:
        messages.error(request, 'Пользователь не найден!')
        return redirect('admin_user_list')
    
    purchases = Purchase.objects.filter(player=player, is_hidden=False).all()
    transactions = Transaction.objects.filter(user=player).order_by('-created_at')[:10]

    if request.method == "POST":
        post_actions = {
            "deactivate_donate_id": "deactivate",
            "unban_id": "unban",
            "hide_donate_id": "hide",
            "restore_donate_id": "restore",
            "charge_amount": "charge",
            "replenishment_amount": "replenishment",
            "hide_nick": "hide_nick",
            "hide_avatar": "hide_avatar",
            "max_money_amount": "max_money",
            "hide_me": "hide_me"
        }

        action_key = next((key for key in post_actions if request.POST.get(key)), None)

        if action_key:
            action = post_actions[action_key]

            match action:
                case "deactivate":
                    donate_id = request.POST.get("deactivate_donate_id")
                    reason = request.POST.get("deactivate_donate_reason")

                    if not reason:
                        messages.error(request, "Вы должны указать причину деактивации доната!")
                        return redirect('admin_user_profile', player.user_id)

                    donate = Purchase.objects.filter(id=donate_id, player=player).first()
                    
                    if not donate:
                        messages.error(request, "Донат не найден!")
                        return redirect('admin_user_profile', player.user_id)

                    donate.is_disabled = True
                    donate.issuer = request.user
                    donate.note = reason
                    donate.save()
                    messages.success(request, "Донат успешно деактивирован")

                case "hide":
                    donate_id = request.POST.get("hide_donate_id")
                    donate = Purchase.objects.filter(id=donate_id, player=player).first()
                    if not donate:
                        messages.error(request, "Донат не найден!")
                        return redirect('admin_user_profile', player.user_id)

                    donate.is_hidden = True
                    donate.save()
                    messages.success(request, "Донат успешно удален")

                case "restore":
                    donate_id = request.POST.get("restore_donate_id")
                    donate = Purchase.objects.filter(id=donate_id, player=player).first()
                    if not donate:
                        messages.error(request, "Донат не найден!")
                        return redirect('admin_user_profile', player.user_id)

                    donate.is_disabled = False
                    donate.is_hidden = False
                    donate.save()
                    messages.success(request, "Донат успешно восстановлен")

                case "charge":
                    amount = int(request.POST.get("charge_amount"))
                    if player.balance >= amount:
                        player.balance -= amount
                        player.save()
                        Transaction.objects.create(user=player, amount=amount, type="charge", reason='Снятие средств администратором')
                        messages.success(request, "Средства успешно сняты")
                    else:
                        messages.warning(request, "У пользователя нет денег")

                case "replenishment":
                    amount = int(request.POST.get("replenishment_amount"))
                    player.balance += amount
                    player.max_money += amount
                    player.save()
                    Transaction.objects.create(user=player, amount=amount, type="replenishment", reason="Выдача средств администратором")
                    messages.success(request, "Средства успешно выданы")

                case "hide_nick":
                    player.hide_nickname()
                    messages.success(request, "Никнейм игрока скрыт")

                case "hide_avatar":
                    player.hide_avatar()
                    messages.success(request, "Аватарка скрыта")

                case "max_money":
                    max_money = int(request.POST.get("max_money_amount"))
                    player.max_money = max_money
                    player.save()
                    messages.success(request, f"Max money изменен на {max_money}")

                case "hide_me":
                    player.is_hidden = not player.is_hidden
                    player.save()
                    if player.is_hidden:
                        messages.success(request, "Ваш аккаунт скрыт с топа донатеров!")
                    else:
                        messages.success(request, "Ваш аккаунт снова может показаться в топе донатеров!")

        return redirect('admin_user_profile', player.user_id)
        
    return render(request, 'user_profile.html', { 
        'player': player, 
        'donates': purchases, 
        'transactions': transactions,
    })

def give_present (request: HttpRequest) -> HttpResponse:
    if not request.user.is_superuser:
        messages.warning(request, 'Куда лезим?)))')
        return redirect('home')
    
    if request.method == 'POST':
        donate_id = request.POST.get("donate_id")
        player_id = request.POST.get("player_id")
        days = request.POST.get("days")
        comment = request.POST.get("comment")

        if not (donate_id and player_id and days and comment):
            messages.warning(request, 'Заполните все поля!')
            redirect('give_present')

        donate = Donate.objects.filter(id=donate_id).first()

        if not donate:
            messages.warning(request, 'Донат не найден!')
            redirect('give_present')

        player = Player.objects.filter(user_id=player_id).first()

        if not player:
            messages.warning(request, 'Игрок не найден!')
            redirect('give_present')

        try:
            days = int(days)
        except ValueError:
            messages.warning(request, 'Время введено не верно!')
            redirect('give_present')

        Present.objects.create(donor=request.user, recipient=player, donate=donate, days=days, comment=comment)

        messages.success(request, 'Подарок успешно выдан!')
        return redirect("give_present")
    
    donates = Donate.objects.all()

    return render(request, 'give_present.html', {
        'donates': donates
    })