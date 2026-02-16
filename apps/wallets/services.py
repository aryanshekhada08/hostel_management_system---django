from .models import WalletTransaction
from apps.notifications.models import Notification
from .utils import send_system_email


def credit_wallet(wallet, amount, description="Admin Added Money"):
    print("CREDIT FUNCTION CALLED")
    # Update balance
    wallet.balance += amount
    wallet.save()

    # Save transaction
    WalletTransaction.objects.create(
        wallet=wallet,
        transaction_type='CREDIT',
        amount=amount,
        description=description
    )

    # Create notification
    Notification.objects.create(
        user=wallet.user,
        title="Wallet Credited 💰",
        message=f"₹{amount} has been added to your wallet."
    )
    print("SENDING EMAIL NOW")
    # Send email
    send_system_email(
        subject="Wallet Credited",
        message=f"""
Dear {wallet.user.full_name},

₹{amount} has been added to your wallet.

Current Balance: ₹{wallet.balance}

Thank you,
Hostel Management Team
        """,
        recipient=wallet.user.email
    )


def debit_wallet(wallet, amount, description="Amount Deducted"):

    if wallet.balance >= amount:

        wallet.balance -= amount
        wallet.save()

        WalletTransaction.objects.create(
            wallet=wallet,
            transaction_type='DEBIT',
            amount=amount,
            description=description
        )

        Notification.objects.create(
            user=wallet.user,
            title="Wallet Debited 💸",
            message=f"₹{amount} has been deducted from your wallet."
        )

        send_system_email(
            subject="Wallet Debited",
            message=f"""
Dear {wallet.user.full_name},

₹{amount} has been deducted from your wallet.

Current Balance: ₹{wallet.balance}

Hostel Management Team
            """,
            recipient=wallet.user.email
        )

        return True

    return False