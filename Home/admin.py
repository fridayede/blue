from django.contrib import admin
from .models import dayclam




# from django.contrib import admin
# from .models import dayclam

# from django.contrib.auth.models import User
# # Register your models here.

# admin.site.register(dayclam)





@admin.register(dayclam)
class DayClaimAdmin(admin.ModelAdmin):
    list_display = ["user", "clicks", "active", "next_available"]
