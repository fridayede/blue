from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from django.utils import timezone
from .manager import CustomUserManager
from common.model import BaseModel
import uuid


class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True,max_length=255)
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True
    )
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD='email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email


class pendingUser(BaseModel):
    
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    verification_code = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)



    def is_valid(self):
        return timezone.now() < self.created_at + timedelta(minutes=10)
    





class TokenType(models.TextChoices):
    PASSWORD_RESET = 'password_reset', 'Password Reset'
    EMAIL_VERIFICATION = 'email_verification', 'Email Verification'


class Token(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50, choices=TokenType.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    

    def is_valid(self):
        return timezone.now() < self.created_at + timezone.timedelta(minutes=20)

    def __str__(self):
        return f"{self.user.email} - {self.token}"



