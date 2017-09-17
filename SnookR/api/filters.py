from main.models import Team, TeamInvite, CustomUser
import rest_framework_filters as filters

character_filters = ['exact', 'contains', 'icontains']


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

    class Meta:
        model = TeamInvite
        fields = ['invitee', 'team', 'status', 'id']
