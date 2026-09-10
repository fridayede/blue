from django.contrib import admin
from .models import  Ads,saveAds,AdAnswer,Adsview


# admin.site.register(saveAds)
admin.site.register(AdAnswer)
admin.site.register(Adsview)




@admin.register(Ads)
class AdsAdmin(admin.ModelAdmin):
    list_display = ["AD_TYPES",'reward_type', "reward"]
@admin.register(saveAds)
class AdsAdmin(admin.ModelAdmin):
    list_display = ["user", "reward_earned","completed_at"]






# Register your models here.
