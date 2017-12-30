from collections import namedtuple
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView, CreateView, RedirectView

from teams.forms import TeamForm
from accounts.models import CustomUser
from teams.models import Team, TeamInvite
from api.serializers import TeamInviteSerializer, TeamSerializer, CustomUserSerializer
from rest_framework.renderers import JSONRenderer


class TeamView(TemplateView, LoginRequiredMixin):
    template_name = 'teams/team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Team.get_all_related(self.request.user)
        context['teams'] = teams
        context['first_team_id'] = teams[0].id if teams else None
        Player = namedtuple('Player', ['team', 'instance', 'status'])

        # Get every player for every team related to the current user
        players = []
        for team in teams:
            for player in team.players.all():
                data = Player(team, player, 'Approved')
                players.append(data)

            # Add the team captain too
            players.append(Player(team, team.team_captain, 'Approved'))

        # Get every invited player for every team
        invites = TeamInvite.objects.filter(team__in=teams)
        for invite in invites:
            print(invite.get_status_display())
            data = Player(invite.team, invite.invitee, invite.get_status_display())
            players.append(data)

        serializer = TeamSerializer(teams, many=True)
        context['teams_json'] = JSONRenderer().render(serializer.data)

        serializer = TeamInviteSerializer(invites, many=True)
        context['invites_json'] = JSONRenderer().render(serializer.data)

        # Wrap players in set() to remove duplicates
        context['players'] = set(players)
        return context


class CreateTeamView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    form_class = TeamForm
    permission_required = 'teams.add_team'
    login_url = '/login/'

    def post(self, request, *args, **kwargs):
        team = Team.objects.create(team_captain=request.user, name=request.POST['name'])
        for k, v in request.POST.items():
            if k.startswith('player-'):
                id = int(v)
                player = CustomUser.objects.get(id=id)
                TeamInvite.objects.create(invitee=player, team=team)

        return redirect('team')


class DeleteTeamView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        team = Team.objects.get(slug=kwargs.get('team'), team_captain=self.request.user, id=kwargs.get('pk'))
        team.delete()
        return reverse('team')
