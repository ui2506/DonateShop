from datetime import timedelta
from django.db import models
from django.utils.timezone import now

from main.models import Player, Server

class Donate(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.JSONField(default=dict)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)
    is_buyable = models.BooleanField(null=False, default=True)
    is_popular = models.BooleanField(null=False, default=False)
    count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} | {self.server.name}"
    
    def update_count(self):
        self.count += 1
        self.save()

class Payment(models.Model):
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[("success", "success"), ("failed", "failed"), ("expired", "expired"), ("refund", "refund"), ("pending", "pending")])
    created_at = models.DateTimeField(auto_now_add=True)
    order_id = models.CharField(max_length=100, unique=True, null=True)
    system_id = models.CharField(max_length=100, unique=True, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}₽ ({self.status})"
    
class Transaction(models.Model):
    user = models.ForeignKey(Player, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=20, choices=[("charge", "charge"), ("replenishment", "replenishment")])
    reason = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount}₽ ({self.type}) - {self.reason}"

class Purchase(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    donate = models.ForeignKey(Donate, on_delete=models.CASCADE)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)

    date_purchased = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    is_disabled = models.BooleanField(null=False, default=False)
    is_hidden = models.BooleanField(null=False, default=False)

    issuer = models.ForeignKey(Player, null=True, blank=True, on_delete=models.SET_NULL, related_name="issued_purchases")
    note = models.CharField(max_length=250, default="", blank=True)

    def save(self, *args, **kwargs):
        if not self.expires_at and hasattr(self.donate, 'duration_days'):
            self.expires_at = now() + timedelta(days=self.donate.duration_days)
        super().save(*args, **kwargs)

    def is_active(self):
        act = self.expires_at is None or self.expires_at > now()
        return act
    
    def __str__(self):
        if not self.is_active() or self.is_disabled:
            return f"{self.player.username} - {self.donate.name} ({self.server.name}) [disabled]"

        return f"{self.player.username} - {self.donate.name} ({self.server.name})"

class Present(models.Model):
    donor = models.ForeignKey(Player, on_delete=models.CASCADE)
    recipient = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="gift_recipient")
    donate = models.ForeignKey(Donate, on_delete=models.CASCADE)
    date_purchased = models.DateTimeField(auto_now_add=True, null=True)
    days = models.IntegerField(default=0)
    comment = models.CharField(default="", max_length=150)
    is_used = models.BooleanField(default=False)
    is_reported = models.BooleanField(default=False)

    def __str__(self):
        donor_id = self.donor.user_id if self.donor else "None"
        recipient_id = self.recipient.user_id if self.recipient else "None"
        return f"is_used: {self.is_used} | {donor_id} -> {recipient_id}"
    
    def use(self):
        Purchase.objects.create(player=self.recipient, donate=self.donate, server=self.donate.server, expires_at=now() + timedelta(days=int(self.days)))

        self.is_used = True
        self.save()

    def cencel(self):
        pass