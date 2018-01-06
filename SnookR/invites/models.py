from django.db import models


class AbstractInvite(models.Model):
    PENDING = 'P'
    APPROVED = 'A'
    DECLINED = 'D'
    STATUS_CHOICES = (
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (DECLINED, 'Declined')
    )

    status = models.CharField(default=PENDING, max_length=1, choices=STATUS_CHOICES)

    class Meta:
        abstract = True


class TeamInvite(AbstractInvite, models.Model):
    invitee = models.ForeignKey('accounts.CustomUser')
    team = models.ForeignKey('teams.Team')

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


class SessionEventInvite(AbstractInvite, models.Model):
    sub = models.ForeignKey('substitutes.Sub')
    team = models.ForeignKey('teams.Team')

    class Meta:
        unique_together = ('sub', 'team')

    def __str__(self):
        return '{} from {} to {}'.format(self.__class__.__name__, self.team, self.sub)
