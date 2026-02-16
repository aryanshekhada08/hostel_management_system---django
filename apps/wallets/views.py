from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import get_user_model

from .models import Wallet
from .services import credit_wallet, debit_wallet   # ✅ Import both here

User = get_user_model()


# ==========================
# STUDENT WALLET DASHBOARD
# ==========================
@login_required
def wallet_dashboard(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.all().order_by('-created_at')

    return render(request, 'wallets/dashboard.html', {
        'wallet': wallet,
        'transactions': transactions
    })

# ==========================
# ADMIN WALLET DASHBOARD
# ==========================
@staff_member_required
def admin_wallet_dashboard(request):
    wallets = Wallet.objects.select_related('user').all()

    return render(request, 'wallets/admin_dashboard.html', {
        'wallets': wallets
    })


# ==========================
# ADMIN ADD MONEY
# ==========================
@staff_member_required
def admin_add_money(request):

    if request.method == 'POST':
        user_id = request.POST.get('user')
        amount = Decimal(request.POST.get('amount'))

        user = User.objects.get(id=user_id)
        wallet = Wallet.objects.get(user=user)

        credit_wallet(wallet, amount, "Admin Added Balance")

        return redirect('admin_wallet_dashboard')  # better redirect

    students = User.objects.filter(role='STUDENT')

    return render(request, 'wallets/admin_add_money.html', {
        'students': students
    })


# ==========================
# ADMIN DEDUCT MONEY
# ==========================
@staff_member_required
def admin_deduct_money(request, user_id):

    wallet = Wallet.objects.get(user_id=user_id)

    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount'))
        debit_wallet(wallet, amount, "Admin Deducted Money")

        return redirect('admin_wallet_dashboard')

    return render(request, 'wallets/admin_deduct.html', {
        'wallet': wallet
    })