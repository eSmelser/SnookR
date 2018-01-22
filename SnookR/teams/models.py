from django.conf import settings
from django.db import models
from django.urls import reverse

from autoslug import AutoSlugField

from invites.models import SessionEventInvite, TeamInvite
from substitutes.models import Sub


class Captain(models.Model):
    """We use this model instead of a Team -> User foreign key because Captains need also have a reference
    to which Division they are in.  Division representatives make captains for their division, and then captains can
    make teams.  A simple foreign key from Team -> User wouldn't account for captains that haven't created any teams yet.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='captain_set')
    division = models.ForeignKey('divisions.Division', related_name='captain_set')

    class Meta:
        unique_together = ('user', 'division')

    def __str__(self):
        return 'Captain: %s' % self.user

class TeamManager(models.Manager):
    def create_team(self, name, captain, players):
        team = self.create(captain=captain, name=name)
        for player in players:
            TeamInvite.objects.create(invitee=player, team=team)

        return team


class Team(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    captain = models.ForeignKey(Captain, null=False, related_name='team_set')
    players = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='team_set')

    objects = TeamManager()

    def __str__(self):
        return self.name

    @staticmethod
    def get_all_related(user):
        if user.is_authenticated():
            combined = list(Team.objects.filter(captain__user=user))
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
    team = models.ForeignKey(Team, related_name='nonuserplayer_set')

    objects = NonUserPlayerManager()

    def __str__(self):
        return self.name
