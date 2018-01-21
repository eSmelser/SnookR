# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING
from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.utils.functional import cached_property

from invites.models import SessionEventInvite


class Sub(models.Model):
    '''
    Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
    willing to sub in a Division.

    Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
    Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
    session containing the dates of a particular session within a division. There are typically 3 sessions
    in a division per year, but the sessions don't necessarily correspond across divisions.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    date = models.DateTimeField('sub date', auto_now=True)
    session_event = models.ForeignKey('divisions.SessionEvent', related_name='sub_set')

    class Meta:
        unique_together = ('user', 'session_event')

    def __str__(self):
        return '<Sub: {} @ {} on {}>'.format(self.user, self.session_event.session.name, self.session_event.date)

    @cached_property
    def session(self):
        return self.session_event.session

    @staticmethod
    def create_from_user(user, date):
        sub, _ = Sub.objects.get_or_create(user=user, date=date)
        return sub

    @property
    def invite_url(self):
        return '/dummy-url/'

    def invitation_requesters(self):
        qs = SessionEventInvite.objects.select_related('team__captain').filter(sub=self)
        return [obj.team.captain for obj in qs]
