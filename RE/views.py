from urllib import request

from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from .models import Referral


@login_required


# def referral(request):
#     try:
#         referral = Referral.objects.get(user=request.user)
#     except Referral.DoesNotExist:
#         referral = None

#     return render(request, "referral.html", {"referral": referral})
def referral(request):
  
    referral, created = Referral.objects.get_or_create(user=request.user)

    referral_link = f"https://t.me/YOUR_BOT_USERNAME/app?startapp={referral.code}"

    return render(request, "referral.html", {
        "referral": referral,
        "referral_link": referral_link
    })
