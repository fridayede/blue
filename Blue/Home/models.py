from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class dayclam(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    clicks = models.IntegerField(default=0,editable=False)
    next_available = models.DateTimeField(default=timezone.now)
    active = models.BooleanField(default=False)
    list_display = ["user", "clicks", "active"]

    def __str__(self):
        return str(self.user)

    def click(self):
        
        self.clicks += 1
        self.save()

    def can_claim(self):
        return timezone.now() >= self.next_available

    def start_timer(self):
        self.next_available = timezone.now() + timedelta(hours=4)  # Set the cooldown period (e.g., 60 seconds)
        self.save()



# class profile(models.Model):
#     user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     total_clicks = models.FloatField(default=0.0)
#     points = models.FloatField(default=0.0)

#     def __str__(self):
#         return str(self.user)