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
    
class Ban(models.Model):
    UNBAN_PRICES = [
        {"min": 0, "max": 5, "price": 200},         # 1–5 часов
        {"min": 5, "max": 24, "price": 300},        # 5–24 часа
        {"min": 24, "max": 48, "price": 400},       # 1–2 дня
        {"min": 48, "max": 168, "price": 500},      # 2–7 дней
        {"min": 168, "max": 720, "price": 700},     # 7 дней–1 месяц
        {"min": 720, "max": 8760, "price": 1000},   # 1 месяц–1 год
        {"min": 8760, "max": 87600, "price": 1500}  # 1–50 лет
    ]

    target_id = models.CharField(max_length=20, null=True)
    target_ip = models.CharField(max_length=15, null=True)
    issuer_id = models.CharField(max_length=20)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    reason = models.CharField(max_length=100)
    is_bought = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True)
    
    def __str__(self):
        return f'{self.target_id} {self.target_ip} <- {self.issuer_id}'
    
    def price(self) -> int:
        duration_hours = (self.expires_at - self.created_at).total_seconds() / 3600

        for rule in self.UNBAN_PRICES:
            if rule["min"] <= duration_hours <= rule["max"]:
                return rule["price"]

        return 2000
    
    def is_active(self):
        return now() < self.expires_at
    
class PlayerXP(models.Model):
    user_id = models.CharField(max_length=32, primary_key=True)
    server_id = models.PositiveSmallIntegerField()
    nickname = models.CharField(max_length=64)

    current_xp = models.PositiveSmallIntegerField(default=0)
    lvl = models.PositiveSmallIntegerField(default=0)
    coins = models.PositiveSmallIntegerField(default=0)

    first_activity = models.DateTimeField()
    last_activity = models.DateTimeField()

    total_rounds = models.PositiveSmallIntegerField(default=0)
    total_seconds = models.PositiveIntegerField(default=0)

    class Meta:
        managed = False
        db_table = "player_xp"

class PlayerPunishment(models.Model):
    UNBAN_PRICES = [
        {"min": 0, "max": 5, "price": 200},         # 1–5 часов
        {"min": 5, "max": 24, "price": 300},        # 5–24 часа
        {"min": 24, "max": 48, "price": 400},       # 1–2 дня
        {"min": 48, "max": 168, "price": 500},      # 2–7 дней
        {"min": 168, "max": 720, "price": 700},     # 7 дней–1 месяц
        {"min": 720, "max": 8760, "price": 1000},   # 1 месяц–1 год
        {"min": 8760, "max": 87600, "price": 1500}  # 1–50 лет
    ]

    TYPE_CHOICES = [
        ('ban', 'Ban'),
        ('mute', 'Mute'),
    ]
        
    id = models.AutoField(primary_key=True)
    target_id = models.CharField(max_length=32)
    issuer_id = models.CharField(max_length=32)
    server_id = models.PositiveIntegerField(null=True, blank=True)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    reason = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_revoked = models.BooleanField(default=False)
    is_buyable = models.BooleanField(default=False)

    def price(self) -> int:
        duration_hours = (self.expires_at - self.created_at).total_seconds() / 3600

        for rule in self.UNBAN_PRICES:
            if rule["min"] <= duration_hours <= rule["max"]:
                return rule["price"]

        return 2000
    
    def is_active(self):
        return now() < self.expires_at

    class Meta:
        managed = False
        db_table = "player_punishment"

class PunishmentHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('extended', 'Extended'),
        ('reduced', 'Reduced'),
        ('revoked', 'Revoked'),
        ('reapplied', 'Reapplied'),
    ]
        
    id = models.AutoField(primary_key=True)
    punishment_id = models.PositiveIntegerField()
    action = models.CharField(max_length=9, choices=ACTION_CHOICES)
    old_expires_at = models.DateTimeField(null=True, blank=True)
    new_expires_at = models.DateTimeField(null=True, blank=True)
    issuer_id = models.CharField(max_length=32)
    reason = models.CharField(max_length=150, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = "punishment_history"