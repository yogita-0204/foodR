from django.contrib import admin

from .models import Profile, Notification, Wallet, WalletTopUp


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "college_id", "created_at")
    list_filter = ("role",)
    search_fields = ("user__username", "college_id")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "notification_type", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("user__username", "title", "message")
    readonly_fields = ("created_at",)


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("profile", "balance", "held_balance", "available_balance", "updated_at")
    search_fields = ("profile__user__username", "profile__user__email")
    readonly_fields = ("created_at", "updated_at", "available_balance")


@admin.register(WalletTopUp)
class WalletTopUpAdmin(admin.ModelAdmin):
    list_display = ("wallet", "amount", "payment_source", "upi_id", "created_at")
    list_filter = ("payment_source", "created_at")
    search_fields = ("wallet__profile__user__username", "upi_id", "reference_id")
    readonly_fields = ("created_at",)
