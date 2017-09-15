from main.models import Team, TeamInvite, CustomUser
import rest_framework_filters as filters


class UserFilter(filters.FilterSet):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username']


def players(request):
    return Team.object.filter(players__id__in=request.data['players']).players.all()


class TeamFilter(filters.FilterSet):
    team_captain = filters.RelatedFilter(UserFilter, name='team_captain', queryset=CustomUser.objects.all())
    players = filters.RelatedFilter(UserFilter, name='players', queryset=players)

    class Meta:
        model = Team
        fields = ['name', 'id']


class TeamInviteFilter(filters.FilterSet):
    pass
