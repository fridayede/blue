from django.contrib import admin
from .models import Referral
# Register your models here.
@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'referred_by', 'referral_count')
    search_fields = ('user__email', 'code', 'referred_by__email')