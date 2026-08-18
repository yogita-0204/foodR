from .models import Notification, Profile, Wallet


def create_notification(user, notification_type, title, message, link=None):
    """
    Helper function to create a notification for a user.
    
    Args:
        user: User object who will receive the notification
        notification_type: Type of notification (from Notification.NOTIFICATION_TYPES)
        title: Short title for the notification
        message: Detailed message
        link: Optional URL to navigate to when notification is clicked
    
    Returns:
        Notification object
    """
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )
    return notification


def get_or_create_wallet(profile):
    if not profile or profile.role != Profile.ROLE_COLLEGE_USER:
        return None

    wallet, _ = Wallet.objects.get_or_create(
        profile=profile,
        defaults={"balance": 0},
    )
    return wallet
