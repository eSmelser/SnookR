import json

from collections import namedtuple
from django.core import serializers
from django.db.models import Q
from django.http import QueryDict
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView, RedirectView, FormView
from django.views.generic.edit import ProcessFormView

from divisions.models import Division
from teams.forms import TeamForm, CaptainForm
from accounts.models import CustomUser
from invites.models import TeamInvite
from teams.models import Team, NonUserPlayer
from api.serializers import TeamInviteSerializer, TeamSerializer, CustomUserSerializer
from rest_framework.renderers import JSONRenderer


class TeamView(PermissionRequiredMixin, LoginRequiredMixin, TemplateView):
    template_name = 'teams/team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Team.get_all_related(self.request.user)

        Player = namedtuple('Player', ['team', 'instance', 'status'])

        # Get every player for every team related to the current user
        players = []
        unregistered_players = []
        for team in teams:
            for player in team.players.all():
                data = Player(team, player, 'Approved')
                players.append(data)

            for unregistered_player in NonUserPlayer.objects.filter(team=team):
                name = unregistered_player.name
                team = unregistered_player.team
                unregistered_players.append({'name': name, 'team': team})

            # Add the team captain too
            players.append(Player(team, team.captain, 'Approved'))

        # Get every invited player for every team
        invites = TeamInvite.objects.filter(team__in=teams)
        for invite in invites:
            data = Player(invite.team, invite.invitee, invite.get_status_display())
            players.append(data)

        serializer = TeamSerializer(teams, many=True)
        context['teams_json'] = JSONRenderer().render(serializer.data)

        serializer = TeamInviteSerializer(invites, many=True)
        context['invites_json'] = JSONRenderer().render(serializer.data)
        context['teams'] = teams
        context['first_team_id'] = teams[0].id if teams else None
        # Wrap players in set() to remove duplicates
        context['players'] = set(players)
        context['unregistered_players'] = unregistered_players
        return context

    def has_permission(self):
        return self.request.user.is_captain()


class CreateTeamView(LoginRequiredMixin, PermissionRequiredMixin, View):
    form_class = TeamForm
    login_url = reverse_lazy('login')

    def post(self, request, *args, **kwargs):
        team = self.create_team()
        NonUserPlayer.objects.create_from_strings(self.request.POST.getlist('unregistered-player'), team=team)
        return redirect('team')

    def get_players(self):
        return CustomUser.objects.filter(id__in=self.request.POST.getlist('player'))

    def has_permission(self):
        division = self.get_division()
        return self.request.user.captain_divisions.filter(pk=division.id).exists()

    def get_division(self):
        pk = self.request.POST.get('division')
        return get_object_or_404(Division, pk=pk)

    def create_team(self):
        request = self.request
        return Team.objects.create_team(
            captain=request.user,
            name=request.POST['team-name'],
            players=self.get_players(),
            division=self.get_division(),
        )


class DeleteTeamView(TemplateView, ProcessFormView):
    template_name = 'teams/delete_team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['team'] = self.get_team()
        return context

    def post(self, request, *args, **kwargs):
        if 'confirm' in self.request.POST:
            team = self.get_team()
            team.delete()

        return redirect(reverse('team'))

    def get_team(self):
        return Team.objects.get(id=self.kwargs.get('pk'))


class AssignTeamCaptainView(LoginRequiredMixin, FormView):
    template_name = 'teams/assign_captain.html'
    form_class = CaptainForm
    success_url = reverse_lazy('assign-team-captain-success')

    def get_initial(self):
        return {'user': self.request.user}

    def form_valid(self, form):
        division = form.cleaned_data['division']
        users = form.cleaned_data['users']
        for user in users:
            user.groups.add(division.team_captain_group)

        division = serializers.serialize('json', [division])
        users = serializers.serialize('json', users)

        self.request.session['division'] = division
        self.request.session['users'] = users
        return super().form_valid(form)


class AssignTeamCaptainSuccessView(LoginRequiredMixin, TemplateView):
    template_name = 'teams/assign_captain_success.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        division = json.loads(self.request.session['division'])[0]
        user = json.loads(self.request.session['users'])

        context['division'] = division
        context['users'] = user

        return context
