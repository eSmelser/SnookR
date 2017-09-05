from django.contrib.auth.models import User
from rest_framework.generics import ListAPIView
from rest_framework.response import Response


class UserListView(ListAPIView):
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [
            {
                'userName': user.username,
                'firstName': user.first_name,
                'lastName': user.last_name,
                'id': user.id
            } for user in queryset
        ]
        return Response(data)
