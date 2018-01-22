from django.conf import settings
from django.db import models

from core.behaviors import Statusable, StatusableQuerySet


class TeamInvite(Statusable, models.Model):
    invitee = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='teaminvite_set')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE, related_name='teaminvite_set')

    objects = StatusableQuerySet.as_manager()

    def __str__(self):
        return 'Invite from {} to {}'.format(self.team, self.invitee)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == self.APPROVED and \
                not self.team.players.filter(username=self.invitee.username).exists():
            self.team.players.add(self.invitee)


class SessionEventInvite(Statusable, models.Model):
    sub = models.ForeignKey('substitutes.Sub', on_delete=models.CASCADE, related_name='sessioneventinvite_set')
    team = models.ForeignKey('teams.Team', on_delete=models.CASCADE)

    objects = StatusableQuerySet.as_manager()

    class Meta:
        unique_together = ('sub', 'team')

    def __str__(self):
        return '{} from {} to {}'.format(self.__class__.__name__, self.team, self.sub)
