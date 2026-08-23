from datetime import timedelta
from donate.models import Purchase
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from DonateShop.utils import get_client_ip
import DonateShop.settings as settings
import json

@api_view(['POST'])
def donators_api(request):
    ip = get_client_ip(request)

    api_key: str = request.headers.get('X-Api-Key')

    print(api_key)

    if api_key not in settings.API_KEY or ip not in settings.API_IP:
        return JsonResponse({'error': 'permission denied'}, status=403)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    user_id: str = data.get('user_id')
    server: str = data.get('server_name')
    donate: str = data.get('donate_name')

    donators = Purchase.objects.filter(is_hidden=False, is_disabled=False, expires_at__gt=timezone.now()).select_related('player', 'donate', 'server').all()

    if user_id:
        donators = donators.filter(player__user_id=user_id)
    if server:
        donators = donators.filter(server__name__iexact=server)
    if donate:
        donators = donators.filter(donate__name__iexact=donate)

    data = {
        "count": donators.count(),
        "results": [
            {
                "user_id": purchase.player.user_id,
                "prefix": {
                    "text": purchase.player.prefix,
                    "color": ""
                },
                "donate": {
                    "donate_name": purchase.donate.name,
                    "server_name": purchase.server.name,
                    "date_purchased": purchase.date_purchased.strftime("%Y-%m-%d %H:%M:%S"),
                    "expires_at": purchase.expires_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "is_active": purchase.is_active() and not purchase.is_disabled,
                }
            }
            for purchase in donators
        ]
    }

    return Response(data)

@api_view(['POST'])
def donators_api_give_days(request):
    ip: str = get_client_ip(request)
    api_key: str = request.headers.get('X-Api-Key')

    if api_key not in settings.API_KEY or ip not in settings.API_IP:
        return Response({'error': 'permission denied'}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return Response({'error': 'Invalid JSON'}, status=400)

    days: str = data.get('days')
    if not days or not str(days).isdigit():
        return Response({'error': 'Invalid days value'}, status=400)

    user_id: str = data.get('user_id')
    server: str = data.get('server_name')
    donate: str = data.get('donate_name')

    donators = Purchase.objects.filter(
        is_hidden=False,
        is_disabled=False,
        expires_at__gt=timezone.now()
    ).select_related('player', 'donate', 'server')

    if user_id:
        donators = donators.filter(player__user_id=user_id)
    if server:
        donators = donators.filter(server__name__iexact=server)
    if donate:
        donators = donators.filter(donate__name__iexact=donate)

    for donator in donators:
        donator.expires_at += timedelta(days=int(days))
        donator.save()

    return Response({
        'status': 'ok',
        'count': donators.count()
    })