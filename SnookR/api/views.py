from rest_framework.generics import ListCreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView
from main.models import Team, CustomUser, TeamInvite, NonUserPlayer, Session, Sub
from api.serializers import (
    TeamInviteSerializer,
    TeamInviteUpdateSerializer,
    TeamSerializer,
    CustomUserSerializer,
    NonUserPlayerSerializer,
    SessionSerializer,
    SubSerializer,
)
from api.permissions import TeamPermission, TeamInvitePermission
from api.filters import TeamFilter, TeamInviteFilter, UserFilter, SessionFilter, SubFilter


class UserView(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def get_object(self):
        return CustomUser.objects.get(username=self.request.user.username)


class UserListView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    filter_class = UserFilter
    filter_fields = ('username', 'id', 'first_name', 'last_name')


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
    filter_class = TeamInviteFilter
    filter_fields = ('invitee', 'team', 'status', 'id')


class TeamInviteUpdateView(UpdateAPIView):
    queryset = TeamInvite.objects.all()
    serializer_class = TeamInviteUpdateSerializer


class NonUserPlayerListCreateView(ListCreateAPIView):
    queryset = NonUserPlayer.objects.all()
    serializer_class = NonUserPlayerSerializer


class SessionListView(ListAPIView):
    serializer_class = SessionSerializer
    queryset = Session.objects.all()
    filter_class = SessionFilter
    filter_fields = tuple(['division'] + list(SessionFilter.Meta.fields.keys()))

    def list(self, request, *args, **kwargs):
        import pdb;pdb.set_trace()
        return super().list(request, *args, **kwargs)


class SubListView(ListAPIView):
    serializer_class = SubSerializer
    queryset = Sub.objects.all()
    filter_class = SubFilter