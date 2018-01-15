from django.db import models
from django.urls import reverse

from autoslug import AutoSlugField

from invites.models import SessionEventInvite, TeamInvite
from substitutes.models import Sub


class TeamManager(models.Manager):
    def create_team(self, name, team_captain, players):
        team = self.create(team_captain=team_captain, name=name)
        for player in players:
            TeamInvite.objects.create(invitee=player, team=team)

        return team


class Team(models.Model):
    '''
    A team can contain many players but should only ever exist in one division
    Team -> Player   : 1 .. *
    Team -> Division : 1
    '''
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team_captain = models.ForeignKey('accounts.CustomUser', related_name='managed_teams')
    players = models.ManyToManyField('accounts.CustomUser', blank=True, related_name='team_set')

    objects = TeamManager()

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_related(user):
        if user.is_authenticated():
            combined = list(Team.objects.filter(team_captain=user))
            combined += list(Team.objects.filter(players=user))
            return sorted(list(set(combined)), key=lambda obj: obj.id)
        else:
            return []

    def get_delete_url(self):
        return reverse('delete-team-confirmation', kwargs={'pk': self.id})

    def add_unregistered_players(self, players):
        for player in players:
            NonUserPlayer.objects.create(name=player['name'], team=self)

    def session_event_invite_subs(self):
        return Sub.objects.filter(session_event__in=SessionEventInvite.objects.filter(team=self))


class NonUserPlayerManager(models.Manager):
    def create_from_strings(self, strings, team):
        return self.bulk_create([self.model(team=team, name=string) for string in strings])


class NonUserPlayer(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team = models.ForeignKey(Team)

    objects = NonUserPlayerManager()

    def __str__(self):
        return self.name
