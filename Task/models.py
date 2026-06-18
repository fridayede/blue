from time import timezone
from django.utils import timezone
from django.db import models
from django.conf import settings





class Ads(models.Model):

    AD_TYPES = (
        ("telegram", "Telegram"),
        ("youtube", "YouTube"),
        ("website", "Website"),
        ("instagram", "Instagram"),
        ("tiktok", "TikTok"),
    )

    # user = models.OneToOneField(
    #     settings.AUTH_USER_MODEL,
    #     on_delete=models.CASCADE
    # )

    title = models.CharField(max_length=200)
    # pls add discription

    ad_type = models.CharField(
        max_length=50,
        choices=AD_TYPES
    )

    link = models.URLField()

    timer = models.IntegerField(default=15)

    REWARD_TYPES =(
        ("blue", "Blue"),
        ("point", "Point"),
        ("usdt", "Usdt"),
    )
    reward_type = models.CharField(
        max_length=50,
        choices=REWARD_TYPES
    )
   


    reward = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    

    

    def __str__(self):
        return self.title



class saveAds(models.Model):
     
     user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
        )
     ad = models.ForeignKey(
        Ads,
        on_delete=models.CASCADE
        )
     reward_earned = models.IntegerField(default=0)
     completed = models.BooleanField(default=False)
    #  completed_at = models.DateTimeField(auto_now_add=True)

         # 🔥 THIS STARTS THE TIMER WHEN USER OPENS TASK
     started_at = models.DateTimeField(default=timezone.now)

     completed_at = models.DateTimeField(null=True, blank=True)

    
     def __str__(self):
        return f"{self.user} saved {self.ad.title}"
    




class AdAnswer(models.Model):
    ad = models.ForeignKey("Ads", on_delete=models.CASCADE)
    answer = models.CharField(max_length=200)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return self.answer