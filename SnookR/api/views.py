import hashlib

from django.db.models import Q
from django.views.generic import TemplateView
from rest_framework.generics import ListCreateAPIView, UpdateAPIView, ListAPIView, RetrieveAPIView, CreateAPIView
from django.core.cache import caches
from rest_framework.response import Response
from substitutes.models import Sub
from divisions.models import Session, SessionEvent
from accounts.models import User
from teams.models import Team, NonUserPlayer
from invites.models import SessionEventInvite, TeamInvite
from messaging.models import Message

from api.serializers import (
    TeamInviteSerializer,
    TeamInviteUpdateSerializer,
    TeamSerializer,
    CustomUserSerializer,
    NonUserPlayerSerializer,
    SessionSerializer,
    SessionEventSerializer,
    SubSerializer,
    SessionEventInviteSerializer,
    MessageSerializer,
    TokenInputSerializer)
from api.permissions import TeamPermission, TeamInvitePermission, MessagePermission
from api.filters import TeamFilter, TeamInviteFilter, UserFilter, SessionFilter, SessionEventFilter, SubFilter, \
    SessionEventInviteFilter, MessageFilter


class UserView(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()

    def get_object(self):
        return User.objects.get(username=self.request.user.username)


class UserSearchView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()

    def list(self, request, *args, **kwargs):
        import pdb;
        pdb.set_trace()


class UserListView(ListAPIView):
    serializer_class = CustomUserSerializer
    queryset = User.objects.all()
    filter_class = UserFilter
    filter_fields = ('username', 'id', 'first_name', 'last_name')


class TeamView(ListCreateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = (TeamPermission,)
    filter_class = TeamFilter
    filter_fields = ('id', 'name')


class TeamInviteListView(ListAPIView):
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


class SubListView(ListCreateAPIView):
    serializer_class = SubSerializer
    queryset = Sub.objects.all()
    filter_class = SubFilter


class SessionEventListView(ListAPIView):
    queryset = SessionEvent.objects.all()
    serializer_class = SessionEventSerializer
    filter_class = SessionEventFilter


class SearchUserView(ListAPIView):
    def list(self, request, *args, **kwargs):
        cache = caches['default']
        query = self.request.GET.get('query', '')
        key = 'search_user_view:%s' % hashlib.md5(query.encode('ascii', 'ignore')).hexdigest()
        objs = cache.get(key)
        if objs is None:
            objs = User.objects.search(query)
            cache.set(key, objs, 60 * 3)

        serializer = CustomUserSerializer(objs, many=True)
        return Response(serializer.data)


class SessionEventInviteListView(ListCreateAPIView):
    queryset = SessionEventInvite.objects.all()
    serializer_class = SessionEventInviteSerializer
    filter_class = SessionEventInviteFilter


class SessionEventInviteView(RetrieveAPIView):
    queryset = SessionEventInvite.objects.all()
    serializer_class = SessionEventInviteSerializer
    filter_class = SessionEventInviteFilter


class MessageListView(ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_class = MessageFilter

    def get_queryset(self):
        return super().get_queryset().filter(Q(sender=self.request.user) | Q(receiver=self.request.user))


class TokenInputListView(ListAPIView):
    serializer_class = TokenInputSerializer

    def list(self, request, *args, **kwargs):
        print('list')
        queryset = self.get_queryset()
        serializer = TokenInputSerializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        q = self.request.GET.get('q', '')
        query = Q()
        for term in q.split(' '):
            query |= Q(first_name__startswith=term) | Q(last_name__startswith=term)

        return User.objects.filter(query)