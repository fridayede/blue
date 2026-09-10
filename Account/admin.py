from django.contrib import admin
from .models import User,pendingUser,Token

# Register your models here.
admin.site.register(User)
admin.site.register(pendingUser)