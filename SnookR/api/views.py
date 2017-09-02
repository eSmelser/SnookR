from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class UserListView(ListAPIView):
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        return Response([user.username for user in queryset])
