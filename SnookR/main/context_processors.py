from main.models import CustomUser


def custom_user(request):
    """Replaces the user key in context with a CustomUser object"""
    try:
        return {'user': CustomUser.objects.get(id=request.user.id)}
    except CustomUser.DoesNotExist:
        return {}