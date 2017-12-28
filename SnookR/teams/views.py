from functools import reduce
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, RedirectView

from main.forms import TeamForm
from teams.models import Team


class TeamView(TemplateView, LoginRequiredMixin):
    template_name = 'teams/team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teams = Team.get_all_related(self.request.user)
        context['teams'] = teams
        context['first_team_id'] = teams[0].id if teams else None
        players = []
        for team in teams:
            for player in team.players.all():
                data = {
                    'team': team,
                    'instance': player,
                }
                players.append(data)

        context['players'] = players
        return context


class CreateTeamView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'teams/create_team.html'
    form_class = TeamForm
    success_url = reverse_lazy('home')
    permission_required = 'main.add_team'
    login_url = '/login/'


class DeleteTeamView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        team = Team.objects.get(slug=kwargs.get('team'), team_captain=self.request.user, id=kwargs.get('pk'))
        team.delete()
        return reverse('team')