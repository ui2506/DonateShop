from django.contrib.auth import get_user_model

import re

def save_steam_id(backend, user, response, *args, **kwargs):
    print(f"[PIPELINE] Backend: {backend.name}, User: {user}, Response: {response}, Type: {type(response)}")  

    if backend.name == "steam" and user is not None:
        claimed_id = response.identity_url if hasattr(response, "identity_url") else None
        if claimed_id:
            steamid_match = re.search(r"/id/(\d+)", claimed_id)
            if steamid_match:
                steamid = steamid_match.group(1)
                user.user_id = steamid
                user.save()
                user.update()
                print(f"[PIPELINE] Сохранён steam_id: {steamid}")
            else:
                print("[PIPELINE] Ошибка: steamid не найден в claimed_id")
        else:
            print("[PIPELINE] Ошибка: response не содержит identity_url")
    else:
        print("[PIPELINE] Ошибка: User не найден!")

User = get_user_model()

def get_or_create_steam_user(backend, uid, user=None, *args, **kwargs):
    """Находит существующего пользователя или создает нового."""

    steam_id = uid.split('/')[-1]
    
    if user:
        return {'user': user}

    existing_user = User.objects.filter(user_id=steam_id).first()

    if existing_user:
        return {'user': existing_user}

    user = User.objects.create(username=f'id_{steam_id}', user_id=steam_id)
    return {'user': user}
