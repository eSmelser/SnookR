from django.db import models
from django.urls import reverse

from autoslug import AutoSlugField


class Team(models.Model):
    '''
    A team can contain many players but should only ever exist in one division
    Team -> Player   : 1 .. *
    Team -> Division : 1
    '''
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team_captain = models.ForeignKey('accounts.CustomUser', related_name="team_captain")
    players = models.ManyToManyField('accounts.CustomUser', blank=True)

    class Meta:
        permissions = (
            ('create_team', 'Can create a team'),
        )

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
        return reverse('delete_team', args=[self.slug, self.id])

    def add_unregistered_players(self, players):
        for player in players:
            NonUserPlayer.objects.create(name=player['name'], team=self)


class NonUserPlayer(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team = models.ForeignKey(Team)

    def __str__(self):
        return self.name