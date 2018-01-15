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


    @property
    def is_closed(self):
        return self.status != AbstractInvite.PENDING

    @staticmethod
    def human_readable_status(status):
        for k, v in AbstractInvite.STATUS_CHOICES:
            if status == k:
                return v

    def approve(self):
        self.status = AbstractInvite.APPROVED
        self.save()


class InviteQuerySet(models.QuerySet):
    def pending(self):
        return self.filter(status=AbstractInvite.PENDING)

    def approved(self):
        return self.filter(status=AbstractInvite.APPROVED)

    def declined(self):
        return self.filter(status=AbstractInvite.DECLINED)


class TeamInvite(AbstractInvite, models.Model):
    invitee = models.ForeignKey('accounts.CustomUser')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)

    objects = InviteQuerySet.as_manager()

    def __str__(self):
        return 'Invite from {} to {}'.format(self.team, self.invitee)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.APPROVED and \
                not self.team.players.filter(username=self.invitee.username).exists():
            self.team.players.add(self.invitee)


class SessionEventInvite(AbstractInvite, models.Model):
    sub = models.ForeignKey('substitutes.Sub', on_delete=models.CASCADE)
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)

    objects = InviteQuerySet.as_manager()

    class Meta:
        unique_together = ('sub', 'team')

    def __str__(self):
        return '{} from {} to {}'.format(self.__class__.__name__, self.team, self.sub)
