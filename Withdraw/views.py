from django.shortcuts import render,redirect
from  Swap.models import Swap
from django.contrib import messages
from django.db.models import Sum
from Task.models import saveAds
from .models import Withdraw
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib import messages
from decimal import Decimal

from .models import Withdraw
from Swap.models import Swap


def withdraw(request):

    user = request.user

    try:
        swap = Swap.objects.get(user=user)
    except Swap.DoesNotExist:
        messages.error(request, "Swap account not found")
        return redirect('Swap:swappage')

    balance = swap.usdt

    print("BALANCE:", balance)

    if request.method == 'POST':

        amount = request.POST.get('withdraw_amount')
        wallet_address = request.POST.get('wallet_address')

        if not wallet_address or not amount:
            messages.error(request, "Please fill in all fields")
            return redirect('Withdraw:withdraw')

        try:
            amount = Decimal(amount)
        except:
            messages.error(request, "Invalid amount")
            return redirect('Withdraw:withdraw')

        if amount > balance:
            messages.error(request, "Insufficient balance")
            return redirect('Withdraw:withdraw')

        if amount < Decimal('2.5'):
            messages.error(request, "Minimum withdrawal amount is 2.5 USDT")
            return redirect('Withdraw:withdraw')

        charge = Decimal('1.0')

        amount_after_charge = amount - charge

        Withdraw.objects.create(
            user=user,
            total_swap=swap,
            wallet_address=wallet_address,
            amount=amount_after_charge,
            status='pending'
        )

        # subtract withdrawn amount from balance
        swap.usdt -= amount
        swap.save()
        withdraws = Withdraw.objects.filter(user=request.user).order_by('-created_at')

        messages.success(request, "Withdrawal request submitted successfully")

        return redirect('Withdraw:withdraw')

    context = {
        'total_swap': balance,
        'status': Withdraw.STATUS_CHOICES,
        'withdraws': Withdraw.objects.filter(user=request.user).order_by('-created_at')
    }

    return render(request, 'withdraw.html', context)