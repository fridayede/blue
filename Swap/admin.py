from django.contrib import admin

# Register your models here.
from .models import Swap

@admin.register(Swap)
class SwapAdmin(admin.ModelAdmin):
    list_display = ["user", "total_amont", "swap_amount", "available_swaps", "available_swaps_amount", "usdt"]