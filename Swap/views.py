from logging import exception
from pyexpat.errors import messages
from django.contrib import messages
from urllib import request

from django.shortcuts import redirect, render

from django.db.models import Sum
from .models import Swap
from Home.models import dayclam
from Task.models import Ads,saveAds




def swappage(request):
    Home = dayclam.objects.all()
    Task = saveAds.objects.all()
    user = request.user

    swap, created = Swap.objects.get_or_create(user=user)
    ads_object = saveAds.objects.filter(user=request.user)

    total_amont = ads_object.aggregate(
        total=Sum('reward_earned')
    )['total'] or 0
    print(total_amont)

    usdt = 0  # ✅ MUST BE HERE (global safe default)

    if request.method == 'POST':

        swap_amount = request.POST.get('swap_points')

        if swap_amount == '' or swap_amount is None:
            messages.error(request, "Please enter an amount")
            return redirect('Swap:swappage')

        swap_amount = int(swap_amount)

        if swap_amount > total_amont:
            messages.error(
                request,
                "Please enter an amount less than or equal to total amount"
            )
            return redirect('Swap:swappage')

        try:
            swap_amount = float(swap_amount)

            usdt = swap_amount / 1000

            tax = swap.tax
            usdt = usdt-(tax) 
            if usdt < 2.5:
                messages.error(request, "Minimum swap value is 2.5 USDT")
                return redirect('Swap:swappage')
            swap.usdt = usdt
            swap.save() 
            ads_object.update(reward_earned=0)
        except ValueError:
            messages.error(request, "Invalid amount")
            return redirect('Swap:swappage')

    return render(request, 'swappage.html', {
        'Home': Home,
        'swap': swap,
        'total_amont': total_amont,
        'usdt': usdt
    })










