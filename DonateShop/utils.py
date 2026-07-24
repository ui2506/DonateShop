import DonateShop.settings as settings
import requests
import re

from django.core.exceptions import ValidationError
from django.http import HttpRequest

def get_steam_user_info(steam_id: str):
    steam_url = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={settings.SOCIAL_AUTH_STEAM_API_KEY}&steamids={steam_id}"
    response = requests.get(steam_url)
    
    if response.status_code == 200:
        data = response.json()
        players = data.get("response", {}).get("players", [])
        
        if players:
            player = players[0]
            raw_nickname = player.get("personaname", "Неизвестно")
            nickname = clean_nickname(raw_nickname)
            avatar = player.get("avatarfull", "")
            
            return nickname, avatar, "ok"
        else:
            return "Пользователь не найден", "", "error"
    else:
        return f"Ошибка: {response.status_code}", "", "error"
    
def clean_nickname(nickname: str) -> str:
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F700-\U0001F77F"
        u"\U0001F780-\U0001F7FF"
        u"\U0001F800-\U0001F8FF"
        u"\U0001F900-\U0001F9FF"
        u"\U0001FA00-\U0001FA6F"
        u"\U0001FA70-\U0001FAFF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)

    cleaned = re.sub(r"[^a-zA-Zа-яА-Я0-9\s.,!?_-]", "", nickname)
    cleaned = emoji_pattern.sub(r'', cleaned)
    return cleaned.strip()
    
def validate_file_size(value):
    max_size = 250 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f"Файл слишком большой! Максимальный размер: {max_size / (1024 * 1024)} MB")
    
def get_client_ip(request: HttpRequest):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    
    return request.META.get('REMOTE_ADDR')

def send_discord_webhook(url: str, message: str) -> None:
    data = {
        'username': 'Webhook Bot',
        'content': message
    }

    requests.post(url, json=data)