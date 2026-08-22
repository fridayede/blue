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

from django.contrib.auth import get_user_model

User = get_user_model()











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
            import time
            from datetime import date

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
from datetime import date, datetime, time
from django.http import JsonResponse,HttpRequest
import time
from datetime import date
from django.views.decorators.csrf import csrf_exempt
from .models import Daily_Ad_count,Adsview
from  Swap.models import Swap

Adsgram_token= "7ce9e22f24ab451f9785c2ceb4132be8"
max_ADS_per_day = 30










# THIRD TESTING
import hmac
import hashlib
import uuid
from datetime import date

from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Import your models safely
# from .models import Daily_Ad_count, Adsview
from Swap.models import Swap














import time, hmac, hashlib, json
from datetime import date

from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from django.shortcuts import render

from .models import Adsview, UserWallet, DailyAdCount

# You can reuse your existing Adsgram_token value here, or generate a new one
AD_TOKEN_SECRET = "7ce9e22f24ab451f9785c2ceb4132be8"

MAX_ADS_PER_DAY = 30
REWARD_PER_AD = 10
MIN_WATCH_SECONDS = 20   # stay just under Monetag's 15s non-skip minimum


@login_required
def point(request):
    return render(request, "point.html")


@login_required
@csrf_exempt
def save_telegram_id(request):
    try:
        data = json.loads(request.body)
        telegram_id = data.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)
        request.user.telegram_id = telegram_id
        request.user.save(update_fields=["telegram_id"])
        return JsonResponse({"status": "success", "telegram_id": telegram_id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# ---- STEP 1: user taps "Watch Video" — creates the token AND a pending row ----
@login_required
def request_ad_token(request):
    user = request.user
    if not user.telegram_id:
        return JsonResponse({"error": True, "message": "Telegram ID not linked"}, status=400)

    today = date.today()
    with transaction.atomic():
        daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
            user=user, date=today, defaults={"count": 0}
        )
        if daily.count >= MAX_ADS_PER_DAY:
            return JsonResponse({
                "error": True,
                "message": "Daily ad limit reached.",
                "remaining": 0
            }, status=400)

        timestamp = int(time.time())
        payload = f"{user.telegram_id}|{timestamp}"
        signature = hmac.new(AD_TOKEN_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        token = f"{payload}|{signature}"

        # ✅ This row is what lets the postback verify a real attempt happened
        Adsview.objects.create(user=user, ymid=token, status='pending')

        return JsonResponse({
            "success": True,
            "ymid": token,
            "watch_seconds": MIN_WATCH_SECONDS,
            "remaining": MAX_ADS_PER_DAY - daily.count
        })


# ---- STEP 2: called ONLY by Monetag's server, never your frontend ----
@csrf_exempt
def monetag_postback(request):
    ymid = request.GET.get("ymid")
    reward_event_type = request.GET.get("value")   # "yes" or "no", per your Monetag dashboard
    event_type = request.GET.get("event")           # "impression" or "click"

    if not ymid:
        return HttpResponse("missing ymid", status=400)

    # ✅ This check was MISSING in your Adsgram version — this is the actual fix
    try:
        telegram_id, ts, signature = ymid.split("|")
        expected_sig = hmac.new(
            AD_TOKEN_SECRET.encode(),
            f"{telegram_id}|{ts}".encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return HttpResponse("bad signature", status=403)
    except ValueError:
        return HttpResponse("malformed ymid", status=400)

    with transaction.atomic():
        try:
            ad_view = Adsview.objects.select_for_update().get(ymid=ymid)
        except Adsview.DoesNotExist:
            return HttpResponse("unknown ymid", status=404)

        if ad_view.status != "pending":
            return HttpResponse("already processed", status=200)  # blocks replay

        if event_type and event_type != "impression":
            return HttpResponse("ignored non-impression event", status=200)

        if reward_event_type not in ("yes", "valued"):
            return HttpResponse("not a rewarded view", status=200)

        elapsed = int(time.time()) - int(ts)
        if elapsed < MIN_WATCH_SECONDS:
            return HttpResponse("too fast, rejected", status=200)

        ad_view.status = "completed"
        ad_view.reward = REWARD_PER_AD
        ad_view.completed_at = timezone.now()
        ad_view.save()

        today = date.today()
        daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
            user=ad_view.user, date=today, defaults={"count": 0}
        )
        daily.count += 1
        daily.save(update_fields=["count"])

        wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=ad_view.user)
        wallet.balance += REWARD_PER_AD
        wallet.save(update_fields=["balance"])

    return HttpResponse("OK", status=200)


# ---- Read-only — safe for the frontend to poll ----
@login_required
def check_ad_status(request):
    ymid = request.GET.get('ymid')
    try:
        ad_view = Adsview.objects.get(ymid=ymid, user=request.user)
    except Adsview.DoesNotExist:
        return JsonResponse({"error": True, "message": "not found"}, status=404)
    return JsonResponse({"status": ad_view.status, "reward": ad_view.reward})










# for adsgram
import json
import uuid
from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import DailyAdCount, Adsview, UserWallet



User = get_user_model()

MAX_ADS_PER_DAY = 30

# How long a pending ad token remains valid
TOKEN_TTL_SECONDS = 60 * 30  # 30 minutes

# Reward for one completed AdsGram ad
ADS_REWARD = 10


@login_required
def requests_ad_token(request):
    user = request.user
    if not user.telegram_id:
        return JsonResponse({"error": True, "message": "Telegram ID not linked"}, status=400)

    today = date.today()
    with transaction.atomic():
        daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
            user=user, date=today, defaults={"count": 0}
        )
        if daily.count >= MAX_ADS_PER_DAY:
            return JsonResponse({
                "error": True,
                "message": "Daily ad limit reached.",
                "remaining": 0
            }, status=400)

        timestamp = int(time.time())
        payload = f"{user.telegram_id}|{timestamp}"
        signature = hmac.new(
            settings.ADSGRAM_SECRET_KEY.encode(),   # define this in settings.py
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        token = f"{payload}|{signature}"

        # ✅ Create an Adsview record (pending)
        ad_view = Adsview.objects.create(
            user=user,
            ymid=token,
            status='pending'
        )

        # ✅ Increment daily count (slot consumed)
        daily.count += 1
        daily.save()

        remaining = MAX_ADS_PER_DAY - daily.count

        return JsonResponse(
            {
        "success": True,
        "ymid": ad_view.ymid,
        "remaining": remaining,
        "reward": ADS_REWARD
    },
    content_type="application/json"
)


# ============================================================
# 2. ADSGRAM REWARD CALLBACK
# ============================================================
@csrf_exempt
def adsgram_postback(request):
    if request.method != "GET":
        return JsonResponse({"error": "GET required"}, status=405)

    ymid = request.GET.get("userId")      # or "ymid"? check AdsGram docs
    reward = request.GET.get("reward", 10)
    # Optional: validate signature if AdsGram sends one

    if not ymid:
        return JsonResponse({"error": "Missing userId"}, status=400)

    try:
        with transaction.atomic():
            ad = Adsview.objects.select_for_update().get(
                ymid=ymid,
                status="pending"
            )
            # Optional: check TTL / expiry
            # if timezone.now() > ad.created_at + timedelta(seconds=TOKEN_TTL_SECONDS):
            #     ad.status = "expired"; ad.save(); return JsonResponse({"error": "Expired"})

            ad.status = "completed"
            ad.reward = reward
            ad.completed_at = timezone.now()
            ad.save()

            user = ad.user
            wallet, _ = UserWallet.objects.get_or_create(user=user)
            wallet.balance += int(reward)
            wallet.save()

            return JsonResponse({"success": True})
    except Adsview.DoesNotExist:
        return JsonResponse({"error": "Invalid ymid"}, status=404)





# def adsgram_postback(request):
#     print("🔥 ADSGRAM POSTBACK HIT")
#     print(request.GET.dict())
#     """
#     AdsGram calls this endpoint when the rewarded ad
#     has been successfully rewarded.

#     Reward URL in AdsGram:

#     https://blue-a7ca.onrender.com/Task/adsgram-postback/?userId=[userId]

#     [userId] is replaced by the Telegram ID.
#     """

#     # AdsGram Reward URL uses GET
#     if request.method != "GET":
#         return HttpResponse(
#             "GET required",
#             status=405
#         )

#     # --------------------------------------------------------
#     # Get Telegram ID from AdsGram
#     # --------------------------------------------------------

#     ymid = request.GET.get("userId")
#     event = request.GET.get("reward_event_type")

#     try:
#         if request.method != 'POST':
#             return JsonResponse({"error": True, "message": "Method not allowed"}, status=405)

#         try:
#             data = json.loads(request.body)
#             ymid = data.get("ymid")
#             reward_amount = data.get("reward", 5)
#         except json.JSONDecodeError:
#             return JsonResponse({"error": True, "message": "Invalid JSON"}, status=400)

#         if not ymid:
#             return JsonResponse({"error": True, "message": "Missing ymid"}, status=400)

#         with transaction.atomic():
#             try:
#                 ad_view = Adsview.objects.select_for_update().get(
#                     ymid=ymid,
#                     user=request.user
#                 )
#             except Adsview.DoesNotExist:
#                 return JsonResponse({"error": True, "message": "Invalid token"}, status=404)

#             if ad_view.status != "pending":
#                 return JsonResponse({"error": True, "message": "Ad already completed"}, status=400)

#             # ... all your remaining validation code ...

#             ad_view.status = "completed"
#             ad_view.reward = reward_amount
#             ad_view.completed_at = timezone.now()
#             ad_view.save()

#             user = request.user
#             user.point_balance += reward_amount
#             user.save()

#             return JsonResponse({
#                 "success": True,
#                 "message": f"Ad completed! +{reward_amount} Blue points",
#                 "new_blue_balance": user.blue_balance
#             })

#     except Exception as e:
#         return JsonResponse({"error": True, "message": str(e)}, status=500)


# ============================================================
# 3. CHECK ADSGRAM AD STATUS
# https://blue-a7ca.onrender.com/Task/adsgram-postback/?userId=[userId]
# ============================================================

@login_required
def ad_status(request):
    """
    Browser uses this endpoint to check whether AdsGram's
    server callback has completed the reward.
    """

    ymid = request.GET.get("ymid")

    if not ymid:
        return JsonResponse(
            {
                "success": False,
                "error": "missing_ymid",
                "message": "Missing ymid."
            },
            status=400
        )

    try:

        ad_view = Adsview.objects.get(
            ymid=ymid,
            user=request.user
        )

    except Adsview.DoesNotExist:

        return JsonResponse(
            {
                "success": False,
                "error": "not_found",
                "message": "Ad not found."
            },
            status=404
        )

    # --------------------------------------------------------
    # Expire old pending token
    # --------------------------------------------------------

    if ad_view.status == "pending":

        if timezone.now() > (
            ad_view.created_at +
            timedelta(seconds=TOKEN_TTL_SECONDS)
        ):

            ad_view.status = "failed"

            ad_view.save(
                update_fields=["status"]
            )

    # --------------------------------------------------------
    # Reward only when server says completed
    # --------------------------------------------------------

    reward = 0

    if ad_view.status == "completed":
        reward = ad_view.reward or ADS_REWARD

    return JsonResponse(
        {
            "success": True,
            "ymid": ad_view.ymid,
            "status": ad_view.status,
            "reward": reward
        }
    )








from django.http import JsonResponse

@login_required
def claim_adsgram_reward(request):
    return JsonResponse({
        "reward": 10,
        "remaining": 29,
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
