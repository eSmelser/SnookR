from django.core.cache import cache

from accounts.models import CustomUser


class CustomUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        return self.get_response(request)

    def process_request(self, request):
        if hasattr(request, 'user') and request.user.is_authenticated():
            cache_key = 'user:%s' % request.user.id
            custom_user = cache.get(cache_key, False)
            if not custom_user:
                custom_user = CustomUser.objects.get(id=request.user.id)
                cache.set(cache_key, custom_user, 60 * 15)  # Cache for 15 minutes

            request.user = custom_user
