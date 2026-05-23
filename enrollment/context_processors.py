from .models import Notification

def notifications_processor(request):

    if request.user.is_authenticated:

        notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]

        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

    else:

        notifications = []
        count = 0

    return {

        'notifications_count': count,
        'notifications_navbar': notifications

    }