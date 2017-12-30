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
    team_captain = models.ForeignKey('main.CustomUser', related_name="team_captain")
    players = models.ManyToManyField('main.CustomUser', blank=True)

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


class TeamInvite(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    DECLINED = 'D'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined')
    )

    status = models.CharField(default=PENDING, max_length=1, choices=STATUS_CHOICES)
    invitee = models.ForeignKey('main.CustomUser')
    team = models.ForeignKey(Team)

    def __str__(self):
        return 'Invite from {} to {}'.format(self.team, self.invitee)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == TeamInvite.APPROVED and \
                not self.team.players.filter(username=self.invitee.username).exists():
            self.team.players.add(self.invitee)

    @property
    def is_closed(self):
        return self.status != TeamInvite.PENDING

    @staticmethod
    def human_readable_status(status):
        for k, v in TeamInvite.STATUS_CHOICES:
            if status == k:
                return v

class NonUserPlayer(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team = models.ForeignKey(Team)

    def __str__(self):
        return self.name