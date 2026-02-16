from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Wallet

@login_required
def wallet_dashboard(request):
    wallet = Wallet.objects.get(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')

    return render(request, 'wallets/dashboard.html', {
        'wallet': wallet,
        'transactions': transactions
    })