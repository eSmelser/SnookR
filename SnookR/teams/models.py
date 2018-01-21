from django.conf import settings
from django.db import models
from django.urls import reverse

from autoslug import AutoSlugField

from invites.models import SessionEventInvite, TeamInvite
from substitutes.models import Sub


class TeamManager(models.Manager):
    def create_team(self, name, captain, players, division):
        team = self.create(captain=captain, name=name, division=division)
        for player in players:
            TeamInvite.objects.create(invitee=player, team=team)

        return team

class Team(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    captain = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, related_name='managedteams_set')
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='team_set')
    division = models.ForeignKey('divisions.Division', null=False, related_name='divisions_set')

    objects = TeamManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.division.make_captain(self.captain)

    @staticmethod
    def get_all_related(user):
        if user.is_authenticated():
            combined = list(Team.objects.filter(captain=user))
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
