from time import timezone
from urllib import request

from django.shortcuts import redirect, render
from django.contrib import messages

from Account.models import User
from .models import Ads,saveAds,AdAnswer
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction


import uuid
import hmac
import hashlib
from django.conf import settings
from django.http import HttpResponse, JsonResponse











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


import uuid
import hmac
import hashlib
from datetime import date, datetime
from django.http import JsonResponse,HttpRequest
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Daily_Ad_count,Adsview
from  Swap.models import Swap

Adsgram_token= "7ce9e22f24ab451f9785c2ceb4132be8"
max_ADS_per_day = 30



def request_ad_token(request):
    # In a real app, get user ID from Telegram authentication
    user = request.GET.get('user')
    today = date.today()
    # ------------------------------------------------------------
    # CHECK DAILY LIMIT
    # ------------------------------------------------------------
    daily, created = Daily_Ad_count.objects.get_or_create(
        user_id=user,
        date=today,
        defaults={'count': 0}
    )

    if daily.count >= max_ADS_per_day:
        # User has already watched 30 ads today
        return JsonResponse({
            'error': True,
            'message': f'You have reached your {max_ADS_per_day} ad limit for today. Come back tomorrow!',
            'remaining': 0
        }, status=400)

    # ------------------------------------------------------------
    # EVERYTHING OK – CREATE A NEW TICKET
    # ------------------------------------------------------------
    ymid = str(uuid.uuid4())
    Adsview.objects.create(user_id=user, ymid=ymid, status='pending')

    return JsonResponse({
        'ymid': ymid,
        'remaining': max_ADS_per_day - daily.count       # how many left for today
    })

































def point(request):
    received_signature = request.headers.get('X-Adsgram-Signature', '')
    computed = hmac.new(
        Adsgram_token.encode('utf-8'),
        request.body,
        hashlib.sha256
    ).hexdigest()
    swap = Swap.objects.get(user=request.user)
    if not hmac.compare_digest(received_signature, computed):
        return JsonResponse({
            "success": False,
            "message": "Invalid signature"
        }, status=400)
     # 2. Read the data
    ymid = request.GET.get('ymid')
    reward_event = request.GET.get('reward_event_type')

    
    # 3. Find our pending record
    try:
        ad_view = Adsview.objects.get(ymid=ymid)
    except Adsview.DoesNotExist:
        return HttpResponse(status=404)
    
     # 4. Reward ONLY if it's valued and still pending
    if reward_event == 'valued' and ad_view.status == 'pending':
        user = ad_view.user
        today = date.today()

        swap.point += 10
        swap.save()
            # increase daily count
        daily, _ = Daily_Ad_count.objects.get_or_create(
            user=user,
            date=today,
            defaults={'count': 0}
        )
        daily.count += 1
        daily.save()

        # ---------- Mark ad view as completed ----------
        ad_view.status = 'completed'
        ad_view.save()

    return JsonResponse({'status': 'ok'})

    

        
    

    user = request.user

    if not user:
        return JsonResponse({
            "success": False,
            "message": "Missing userId"
        }, status=400)

    try:
        user = User.objects.get(user=user)

        user.views += 10
        user.save()

        return JsonResponse({
            "success": True,
            "views": user.views
        })
    except User.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "User not found"
        }, status=404)
    return render(request, "point.html")










































@login_required
def complect(request):

    completed_tasks = saveAds.objects.filter(
        user=request.user,
        completed=True
    )

    return render(request, "complect.html", {
        "completed_tasks": completed_tasks
    })
