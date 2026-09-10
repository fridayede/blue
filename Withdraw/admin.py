from django.contrib import admin
from .models import Withdraw
# Register your models here.


@admin.register(Withdraw)
class WithdrawAdmin(admin.ModelAdmin):
    list_display = ["user", "amount", "created_at","paid_at", "status"]
    list_filter = ('status',)