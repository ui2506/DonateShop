from datetime import timedelta
from donate.models import Purchase
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.decorators import api_view
from DonateShop.utils import get_client_ip
from main.models import Ban, Server
from django.db.models import Q
import DonateShop.settings as settings
import requests
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

@api_view(['POST'])
def ban(request):
    ip = get_client_ip(request)
    api_key = request.headers.get('X-Api-Key')

    if not (api_key in settings.API_KEY and ip in settings.API_IP):
        return Response({'error': 'permission denied'}, status=403)

    data = request.data
    required_fields = ['duration', 'target_id', 'target_ip', 'issuer_id', 'reason', 'server_name']
    if not all(field in data for field in required_fields):
        return Response({'error': 'Missing required fields'}, status=400)

    try:
        duration = int(data['duration'])
    except (ValueError, TypeError):
        return Response({'error': 'Invalid duration'}, status=400)

    expires_at = timezone.now() + timedelta(seconds=duration)

    server = Server.objects.filter(name=data['server_name']).first()
    if not server:
        return Response({'error': 'Server not found'}, status=404)

    Ban.objects.create(
        target_id=data['target_id'],
        target_ip=data['target_ip'],
        issuer_id=data['issuer_id'],
        server=server,
        reason=data['reason'],
        expires_at=expires_at
    )

    return Response({'status': 'ok'})

@api_view(['POST'])
def unban(request):
    ip = get_client_ip(request)
    api_key = request.headers.get('X-Api-Key')

    if not (api_key in settings.API_KEY and ip in settings.API_IP):
        return Response({'error': 'permission denied'}, status=403)

    user_id = request.data.get('user_id')
    user_ip = request.data.get('user_ip')

    ban = Ban.objects.filter(Q(target_id=user_id) | Q(target_ip=user_ip))

    if not ban:
        return Response({
            'status': 'not-found',
        }, status=404)
    
    ban.delete()
    
    return Response({
        'status': 'ok',
    })

@api_view(['POST'])
def check_ban(request):
    ip = get_client_ip(request)
    api_key = request.headers.get('X-Api-Key')

    if api_key not in settings.API_KEY or ip not in settings.API_IP:
        return Response({'error': 'permission denied'}, status=403)

    user_id = request.data.get('user_id')
    user_ip = request.data.get('user_ip')

    ban = Ban.objects.filter(
        Q(target_id=user_id) | Q(target_ip=user_ip),
        expires_at__gt=timezone.now(),
        is_bought=False
    ).last()

    if ban:
        return Response({
            'status': 'ok',
            'is_banned': True,
            'expires_at': ban.expires_at,
            'reason': ban.reason
        })

    return Response({
        'status': 'ok',
        'is_banned': False
    })

def proxy_server_data(request, scpsl_id):
    api_url = f"https://api.scplist.kr/api/servers/{scpsl_id}"
    
    try:
        response = requests.get(api_url, timeout=5)
        return JsonResponse(response.json(), safe=False)
    except requests.exceptions.RequestException as e:
        return JsonResponse({'error': f'Ошибка API: {str(e)}'}, status=500)
