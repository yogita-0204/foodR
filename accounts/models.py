from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Profile(models.Model):
    ROLE_COLLEGE_USER = "college_user"
    ROLE_SHOP_OWNER = "shop_owner"

    ROLE_CHOICES = [
        (ROLE_COLLEGE_USER, "College User"),
        (ROLE_SHOP_OWNER, "Shop Owner"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    college_id = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.role == self.ROLE_COLLEGE_USER and not self.college_id:
            raise ValidationError({"college_id": "College ID is required for college users."})

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Wallet(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    held_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def available_balance(self):
        return self.balance - self.held_balance

    def hold_amount(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            return
        if self.available_balance < amount:
            raise ValidationError("Insufficient wallet balance.")
        self.held_balance += amount
        self.save(update_fields=["held_balance", "updated_at"])

    def debit_amount(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            return
        if self.balance < amount:
            raise ValidationError("Insufficient wallet balance.")
        self.balance -= amount
        self.save(update_fields=["balance", "updated_at"])

    def credit_amount(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            return
        self.balance += amount
        self.save(update_fields=["balance", "updated_at"])

    def release_amount(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            return
        self.held_balance = max(Decimal("0.00"), self.held_balance - amount)
        self.save(update_fields=["held_balance", "updated_at"])

    def __str__(self):
        return f"Wallet - {self.profile.user.username}"


class WalletTopUp(models.Model):
    SOURCE_PHONEPE = "phonepe"
    SOURCE_PAYTM = "paytm"
    SOURCE_GOOGLE_PAY = "google_pay"
    SOURCE_OTHER = "other"

    SOURCE_CHOICES = [
        (SOURCE_PHONEPE, "PhonePe"),
        (SOURCE_PAYTM, "Paytm"),
        (SOURCE_GOOGLE_PAY, "Google Pay"),
        (SOURCE_OTHER, "Other UPI App"),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="topups")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_source = models.CharField(max_length=20, choices=SOURCE_CHOICES)
    upi_id = models.CharField(max_length=100, blank=True, null=True)
    reference_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Top-up ₹{self.amount} via {self.get_payment_source_display()}"


class Notification(models.Model):
    NOTIFICATION_ORDER_PLACED = "order_placed"
    NOTIFICATION_ORDER_PREPARING = "order_preparing"
    NOTIFICATION_ORDER_READY = "order_ready"
    NOTIFICATION_ORDER_COMPLETED = "order_completed"
    NOTIFICATION_ORDER_CANCELLED = "order_cancelled"
    NOTIFICATION_FEEDBACK_RECEIVED = "feedback_received"
    NOTIFICATION_TIME_EXTENDED = "time_extended"

    NOTIFICATION_TYPES = [
        (NOTIFICATION_ORDER_PLACED, "New Order Placed"),
        (NOTIFICATION_ORDER_PREPARING, "Order Being Prepared"),
        (NOTIFICATION_ORDER_READY, "Order Ready for Pickup"),
        (NOTIFICATION_ORDER_COMPLETED, "Order Completed"),
        (NOTIFICATION_ORDER_CANCELLED, "Order Cancelled"),
        (NOTIFICATION_FEEDBACK_RECEIVED, "Feedback Received"),
        (NOTIFICATION_TIME_EXTENDED, "Pickup Time Extended"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title}"
