from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.timezone import now
from DonateShop.utils import get_steam_user_info

class Player(AbstractUser):
    user_id = models.CharField(null=True, max_length=20, unique=True)
    last_update = models.DateTimeField(null=True, blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    avatar = models.URLField(null=True, blank=True)
    nickname = models.CharField(max_length=50, default="")
    max_money = models.PositiveIntegerField(default=0)
    is_hidden_nickname = models.BooleanField(default=False)
    is_hidden_avatar = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)
    prefix = models.CharField(max_length=20, default='', blank=True)

    groups = models.ManyToManyField(
        Group,
        related_name="player_%(class)s_related",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="player_%(class)s_related",
        blank=True
    )

    def hide_nickname(self):
        if self.is_hidden_nickname:
            self.is_hidden_nickname = False
        else:
            self.is_hidden_nickname = True

        self.update()

    def hide_avatar(self):
        if self.is_hidden_avatar:
            self.is_hidden_avatar = False
        else:
            self.is_hidden_avatar = True
            
        self.update()

    def update(self):
        if self.is_hidden_nickname and self.is_hidden_avatar:
            self.nickname = "Скрыт"
            self.avatar = "https://avatars.fastly.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
            self.save()
            return

        nick, photo, status = get_steam_user_info(self.user_id)

        if self.is_hidden_nickname:
            self.nickname = "Скрыт"
        elif status == 'ok':
            self.nickname = nick
        
        if self.is_hidden_avatar:
            self.avatar = "https://avatars.fastly.steamstatic.com/fef49e7fa7e1997310d705b2a6158ff8dc1cdfeb_full.jpg"
        elif status == 'ok':
            self.avatar = photo

        if status == 'ok':
            self.last_update = now()
        
        self.save()
        
class Server(models.Model):
    name = models.CharField(max_length=50, unique=True)
    server_name = models.CharField(max_length=1000, null=True)
    server_id = models.IntegerField(default=0)
    scpsl_id = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name}"
    
class DonateRule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class GameRule(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.title

class Rule(models.Model):
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    donate_rules = models.ForeignKey(DonateRule, on_delete=models.CASCADE, null=True)
    game_rules = models.ForeignKey(GameRule, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.server.name