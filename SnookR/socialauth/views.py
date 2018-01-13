from django.http import HttpResponse
from django.views.generic import View


class FacebookAuthView(View):
    def post(self, request, *args, **kwargs):
        print(self, request, args, kwargs)
        print(request.POST)
        return HttpResponse('Posted')