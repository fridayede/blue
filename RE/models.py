from django.db import models

# Create your models here.
import uuid
from django.db import models
from django.conf import settings


class Referral(models.Model):

    # 👇 this uses YOUR custom user model
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True
    )

    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='referrals'
    )

    referral_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):

        if not self.code:
            self.code = str(uuid.uuid4())[:8]

        super().save(*args, **kwargs)

    def __str__(self):
        return self.user.email