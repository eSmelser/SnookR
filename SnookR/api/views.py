from django.urls import reverse
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, CreateAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from main.models import Team, CustomUser, TeamInvite
from api.serializers import TeamInviteSerializer, TeamSerializer, CustomUserSerializer
from api.permissions import TeamPermission, TeamInvitePermission
from api.filters import TeamFilter

class UserListView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()


class TeamView(ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (TeamPermission,)
    filter_class = TeamFilter
    filter_fields = ('id', 'name')


class TeamInviteListView(ListCreateAPIView):
    queryset = TeamInvite.objects.all()
    serializer_class = TeamInviteSerializer
    permission_classes = (TeamInvitePermission,)