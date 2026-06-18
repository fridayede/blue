from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import timedelta
from .models import dayclam


@login_required
def clam(request):
    

    user = request.user
    print(user)

    # get user record
    claim = dayclam.objects.filter(user=user).first()

    # create record if user does not have one
    if not claim:
        claim = dayclam.objects.create(
            user=user,
            clicks=0
        )

    if request.method == "POST":

        # check timer
        if claim.next_available and timezone.now() < claim.next_available:
            messages.error(request, "Wait for the timer to finish.")
            return redirect("/Home/clam/")

        # increase clicks
        claim.clicks += 1

        # next claim time
        # claim.next_available = timezone.now() + timedelta(hours=24)
        claim.next_available = timezone.now() + timedelta(hours=4)  # Set the cooldown period (e.g., 60 seconds)

        # save to database
        claim.save()

        messages.success(request, "Claim successful!")

        return redirect("/Home/clam/")

    return render(request, "clam.html", {
        "clicks": claim.clicks,
        "next_available": claim.next_available,
    })