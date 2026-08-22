from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from Swap.models import Swap

class Withdraw(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='withdraws')

    total_swap = models.ForeignKey(Swap, on_delete=models.CASCADE, null=True, blank=True)

    wallet_address = models.CharField(max_length=255)

    amount = models.DecimalField(max_digits=20, decimal_places=8)

    charge =models.IntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, 
                              choices=STATUS_CHOICES,
                                default='pending'
                                )
    paid_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Withdraw by {self.user} - {self.amount} USDT"

