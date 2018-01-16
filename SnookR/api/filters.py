from substitutes.models import Sub
from divisions.models import Division, Session, SessionEvent
from accounts.models import CustomUser
from teams.models import Team
from invites.models import TeamInvite, SessionEventInvite
from messaging.models import Message
import rest_framework_filters as filters

character_filters = ['exact', 'contains', 'icontains', 'startswith']
time_filters = ['exact', 'gt', 'gte', 'lt', 'lte']


class UserFilter(filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = {
            'id': ['exact'],
            'first_name': character_filters,
            'last_name': character_filters,
            'username': character_filters,

        }


def players(request):
    return Team.object.filter(players__id__in=request.data['players']).players.all()


class TeamFilter(filters.FilterSet):
    team_captain = filters.RelatedFilter(UserFilter, name='team_captain', queryset=CustomUser.objects.all())
    players = filters.RelatedFilter(UserFilter, name='players', queryset=players)

    class Meta:
        model = Team
        fields = ['name', 'id']


class TeamInviteFilter(filters.FilterSet):
    invitee = filters.RelatedFilter(UserFilter, name='invitee', queryset=CustomUser.objects.all())
    team = filters.RelatedFilter(TeamFilter, name='team', queryset=Team.objects.all())
    status = filters.CharFilter(name='status')


class DivisionFilter(filters.FilterSet):
    class Meta:
        model = Division
        fields = {
            'name': character_filters,
            'slug': ['exact'],
        }


class SessionFilter(filters.FilterSet):
    division = filters.RelatedFilter(DivisionFilter, name='division', queryset=Division.objects.all())

    # subs = filters.RelatedFilter(SubFilter, name='subs', queryset=Sub.objects.all())

    class Meta:
        model = Session
        fields = {
            'name': character_filters,
            'game': character_filters,
            'start_date': time_filters,
            'end_date': time_filters,
            'slug': ['exact'],
        }


class SessionEventFilter(filters.FilterSet):
    session = filters.RelatedFilter(SessionFilter, name='session', queryset=Session.objects.all())

    class Meta:
        model = SessionEvent
        fields = {
            'date': time_filters,
            'start_time': time_filters,
            'id': ['exact'],
        }


class SubFilter(filters.FilterSet):
    user = filters.RelatedFilter(UserFilter, name='user', queryset=CustomUser.objects.all())
    session_event = filters.RelatedFilter(SessionEventFilter, name='session_event', queryset=SessionEvent.objects.all())

    class Meta:
        model = Sub
        fields = ['user', 'session_event']


class SessionEventInviteFilter(filters.FilterSet):
    invitee = filters.RelatedFilter(SubFilter, name='invitee', queryset=Sub.objects.all())
    event = filters.RelatedFilter(SessionEventFilter, name='event', queryset=SessionEvent.objects.all())

    class Meta:
        model = SessionEventInvite
        fields = ['invitee', 'event']


class MessageFilter(filters.FilterSet):
    sender = filters.RelatedFilter(UserFilter, name='sender', queryset=CustomUser.objects.all())
    receiver = filters.RelatedFilter(UserFilter, name='receiver', queryset=CustomUser.objects.all())
    id__gt = filters.NumberFilter(name='id', lookup_expr='gt')
    id__lt = filters.NumberFilter(name='id', lookup_expr='lt')

    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'timestamp', 'text', 'id']
