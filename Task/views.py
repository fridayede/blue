from time import timezone
from urllib import request

from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Ads,saveAds,AdAnswer
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction











def hometask(request):

    ads = Ads.objects.all()

    ads = Ads.objects.exclude(
        saveads__user=request.user,
        saveads__completed=True
    )


    return render(request, "hometask.html", {
        "ads": ads
    })









@login_required
def task(request, id):

    # STEP 1: get the single task
    ad = get_object_or_404(Ads, id=id)

    # STEP 2: check if already completed
    already_completed = saveAds.objects.filter(
        user=request.user,
        ad=ad,
        completed=True
    ).exists()

    # STEP 3: if completed → send to complect
    if already_completed:
        return redirect("Task:complect")

    # STEP 3B: get or create timer record (START TIME)
    user_task = saveAds.objects.filter(
        user=request.user,
        ad=ad
    ).first()

    if not user_task:
        user_task = saveAds.objects.create(
            user=request.user,
            ad=ad,
            reward_earned=0,
            completed=False
        )

    # STEP 4: handle form submit
    if request.method == "POST":

        user_answer = request.POST.get("user_answer", "").strip()

        if not user_answer:
            messages.error(request, "Please enter an answer.")
            return redirect("Task:task", id=ad.id)

        # 🔥 TIMER CHECK (IMPORTANT ADDITION)
        from django.utils import timezone

        time_passed = timezone.now() - user_task.started_at

        if time_passed.seconds < ad.timer:
            messages.error(
                request,
                f"Wait {ad.timer - time_passed.seconds} seconds before submitting."
            )
            return redirect("Task:task", id=ad.id)

        try:
            with transaction.atomic():

                # STEP 5: check answer
                answer_obj = AdAnswer.objects.filter(
                    ad=ad,
                    answer__iexact=user_answer
                ).first()

                if not answer_obj:
                    messages.error(request, "Wrong answer.")
                    return redirect("Task:task", id=ad.id)

                # STEP 6: save completion + reward
                user_task.completed = True
                user_task.reward_earned = ad.reward
                user_task.save()

                messages.success(
                    request,
                    f"Correct answer! You earned {ad.reward} 🎉"
                )

                return redirect("Task:complect")

        except Exception as e:
            print(e)
            messages.error(request, "Something went wrong.")

    return render(request, "task.html", {
        "ad": ad,
        "timer": ad.timer
    })














@login_required
def complect(request):

    completed_tasks = saveAds.objects.filter(
        user=request.user,
        completed=True
    )

    return render(request, "complect.html", {
        "completed_tasks": completed_tasks
    })
