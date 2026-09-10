from django.db import models


from django.conf import settings
from django.contrib.auth.models import User
from Task.models import Ads,saveAds

# Create your models here.

class Swap(models.Model):
    # done
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # total balance in points

    ads_reward = models.ForeignKey(saveAds, on_delete=models.CASCADE, null=True, blank=True)
    total_amont = models.IntegerField(default=0, editable=False)
    # amount to be swapped/// done
    swap_amount = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    # if the amont is more than 2.9 dollars
    available_swaps = models.IntegerField(default=0, editable=False)
    # balance in points//done
    available_swaps_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    usdt = models.DecimalField(max_digits=20, decimal_places=8, default=0.0)
    tax =models.IntegerField(default=2)
    list_display = ["user", "total_swaps","usdt"]


   


    def save(self, *args, **kwargs):
        if self.ads_reward:
            self.total_amont = self.ads_reward.reward_earned
        else:
            self.total_amont = 0

        super().save(*args, **kwargs)


    def __str__(self):
        return str(self.user)
    
    def __str__(self):
        return str(self.usdt)




