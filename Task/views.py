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

Adsgram_token = "7ce9e22f24ab451f9785c2ceb4132be8"
max_ADS_per_day = 30


@login_required
def point(request: HttpRequest) -> HttpResponse:
    """Renders the standard user points interface page."""
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
    



import uuid
import hmac
import hashlib
from datetime import date
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import time
from datetime import date
from .models import AdView, UserWallet, DailyAdCount,Daily_Ad_count, Adsview


from django.db import transaction
# from django.http import JsonResponse, HttpResponse
# from django.views.decorators.csrf import csrf_exempt
from datetime import date
# import uuid
# import hmac
# import hashlib
import json



MAX_ADS_PER_DAY = 50          # you can change this number anytime
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
        signature = hmac.new(
            Adsgram_token.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        token = f"{payload}|{signature}"

        return JsonResponse({
            "success": True,
            "ymid": token,
            "remaining": MAX_ADS_PER_DAY - daily.count
        })

# @csrf_exempt
# @transaction.atomic
# def adsgram_postback(request):
#     telegram_id = request.GET.get("userId")

#     print("ADSGram postback received:", telegram_id)

#     if not telegram_id:
#         return HttpResponse("Missing userId", status=400)

#     try:
#         user = User.objects.select_for_update().get(
#             telegram_id=telegram_id
#         )
#     except User.DoesNotExist:
#         return HttpResponse("User not found", status=404)

#     today = date.today()

#     daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
#         user=user,
#         date=today,
#         defaults={"count": 0}
#     )

#     if daily.count >= MAX_ADS_PER_DAY:
#         return HttpResponse("Daily limit reached", status=400)

#     wallet, _ = UserWallet.objects.select_for_update().get_or_create(
#         user=user
#     )

#     wallet.balance += 10
#     wallet.save()

#     daily.count += 1
#     daily.save()

#     print(
#         "Reward added:",
#         user.email,
#         "Telegram ID:",
#         user.telegram_id
#     )

#     return JsonResponse({
#         "status": "ok",
#         "message": "Reward added"
#     })

@csrf_exempt
@transaction.atomic
def adsgram_postback(request):

     
    print("🔥 ADSGRAM CALLBACK RECEIVED")
    print("GET DATA:", request.GET)
    print("POST DATA:", request.POST)

    token = request.GET.get("userId")
    print("Token extracted:", token)

    if not token:
        return JsonResponse({"error": "Missing token"}, status=400)

    try:
        parts = token.split('|')
        if len(parts) != 3:
            raise ValueError("Invalid token format")
        telegram_id, timestamp_str, signature = parts
        timestamp = int(timestamp_str)
        if time.time() - timestamp > 300:
            return JsonResponse({"error": "Token expired"}, status=400)
        payload = f"{telegram_id}|{timestamp_str}"
        expected = hmac.new(
            Adsgram_token.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
        if not hmac.compare_digest(signature, expected):
            return JsonResponse({"error": "Invalid signature"}, status=400)
    except Exception as e:
        print("Token verification error:", e)
        return JsonResponse({"error": "Invalid token"}, status=400)

    try:
        user = User.objects.select_for_update().get(telegram_id=telegram_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    today = date.today()
    daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
        user=user, date=today, defaults={"count": 0}
    )
    if daily.count >= MAX_ADS_PER_DAY:
        return JsonResponse({"error": "Daily limit reached"}, status=400)

    wallet, _ = UserWallet.objects.select_for_update().get_or_create(user=user)
    wallet.balance += 10
    wallet.save()
    daily.count += 1
    daily.save()

    return JsonResponse({"status": "success", "message": "Reward added"})



























# @transaction.atomic
# def adsgram_postback(request):
#     email = request.GET.get("userId")

#     if not email:
#         return HttpResponse("Missing userId", status=400)

#     try:
#         user = User.objects.select_for_update().get(email=email)
#     except User.DoesNotExist:
#         return HttpResponse("User not found", status=404)

#     print("Reward for:", user.email)

#     # 1. Verify webhook signature
#     received_signature = request.headers.get('X-Adsgram-Signature', '')
#     computed = hmac.new(
#         Adsgram_token.encode('utf-8'),
#         request.body,
#         hashlib.sha256
#     ).hexdigest()
    
#     if not hmac.compare_digest(computed, received_signature):
#         return HttpResponse("Invalid signature", status=400)

#     # 2. Extract Data
#     ymid = request.GET.get("userId")
#     reward_event = request.GET.get('reward_event_type')

#     if not ymid or not reward_event:
#         try:
#             body_data = json.loads(request.body)
#             ymid = body_data.get('ymid')
#             reward_event = body_data.get('reward_event_type')
#         except json.JSONDecodeError:
#             return HttpResponse("Invalid Payload", status=400)

#     # 3. Find pending record with a lock
#     try:
#         ad_view = AdView.objects.select_for_update().get(ymid=ymid)
#     except AdView.DoesNotExist:
#         return HttpResponse("Ad tracking ID not found", status=404)

#     # 4. Process reward securely if pending
#     if reward_event == 'valued' and ad_view.status == 'pending':
#         user_id = ad_view.user_id 
#         today = date.today()

#         daily, _ = DailyAdCount.objects.select_for_update().get_or_create(
#             user_id=user_id,
#             date=today,
#             defaults={'count': 0}
#         )
        
#         if daily.count >= MAX_ADS_PER_DAY:
#             ad_view.status = 'failed_limit_exceeded'
#             ad_view.save()
#             return HttpResponse("Daily limit already reached", status=400)

#         daily.count += 1
#         daily.save()

#         wallet, _ = UserWallet.objects.select_for_update().get_or_create(user_id=user_id)
#         wallet.balance += 10
#         wallet.save()

#         ad_view.status = 'completed'
#         ad_view.save()

#     return JsonResponse({'status': 'ok'})
























# def point(request):
#     received_signature = request.headers.get('X-Adsgram-Signature', '')
#     computed = hmac.new(
#         Adsgram_token.encode('utf-8'),
#         request.body,
#         hashlib.sha256
#     ).hexdigest()
#     swap = Swap.objects.get(user=request.user)
#     if not hmac.compare_digest(received_signature, computed):
#         return JsonResponse({
#             "success": False,
#             "message": "Invalid signature"
#         }, status=400)
#      # 2. Read the data
#     ymid = request.GET.get('ymid')
#     reward_event = request.GET.get('reward_event_type')

    
#     # 3. Find our pending record
#     try:
#         ad_view = Adsview.objects.get(ymid=ymid)
#     except Adsview.DoesNotExist:
#         return HttpResponse(status=404)
    
#      # 4. Reward ONLY if it's valued and still pending
#     if reward_event == 'valued' and ad_view.status == 'pending':
#         user = ad_view.user
#         today = date.today()

#         swap.point += 10
#         swap.save()
#             # increase daily count
#         daily, _ = Daily_Ad_count.objects.get_or_create(
#             user=user,
#             date=today,
#             defaults={'count': 0}
#         )
#         daily.count += 1
#         daily.save()

#         # ---------- Mark ad view as completed ----------
#         ad_view.status = 'completed'
#         ad_view.save()

#     # return JsonResponse({'status': 'ok'})

    

        
    

#     # user = request.user

#     # if not user:
#     #     return JsonResponse({
#     #         "success": False,
#     #         "message": "Missing userId"
#     #     }, status=400)

#     # try:
#     #     user = User.objects.get(user=user)

#     #     user.views += 10
#     #     user.save()

#     #     return JsonResponse({
#     #         "success": True,
#     #         "views": user.views
#     #     })
#     # except User.DoesNotExist:
#     #     return JsonResponse({
#     #         "success": False,
#     #         "message": "User not found"
#     #     }, status=404)
#     return render(request, "point.html")







# def point(request):
#     # Verify AdsGram signature
#     received_signature = request.headers.get("X-Adsgram-Signature", "")

#     computed = hmac.new(
#         Adsgram_token.encode("utf-8"),
#         request.body,
#         hashlib.sha256
#     ).hexdigest()

#     if not hmac.compare_digest(received_signature, computed):
#         return HttpResponse("Invalid signature", status=400)

#     # Read AdsGram data
#     ymid = request.GET.get("ymid")
#     reward_event = request.GET.get("reward_event_type")

#     # Find the pending ad record
#     try:
#         ad_view = Adsview.objects.get(ymid=ymid)
#     except Adsview.DoesNotExist:
#         return HttpResponse("Ad not found", status=404)

#     # Reward only once
#     if reward_event == "valued" and ad_view.status == "pending":
#         user = ad_view.user
#         today = date.today()

#         # Update user's points
#         swap = Swap.objects.get(user=user)
#         swap.point += 10
#         swap.save()

#         # Update daily ad count
#         daily, created = Daily_Ad_count.objects.get_or_create(
#             user=user,
#             date=today,
#             defaults={"count": 0},
#         )
#         daily.count += 1
#         daily.save()

#         # Mark as completed
#         ad_view.status = "completed"
#         ad_view.save()

#     # Tell AdsGram everything was processed successfully
#     return HttpResponse(status=200)






































@login_required
def complect(request):

    completed_tasks = saveAds.objects.filter(
        user=request.user,
        completed=True
    )

    return render(request, "complect.html", {
        "completed_tasks": completed_tasks
    })
