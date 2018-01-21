from accounts.models import User


def custom_user(request):
    """Replaces the user key in context with a CustomUser object"""
    try:
        return {'user': User.objects.get(id=request.user.id)}
    except User.DoesNotExist:
        return {}