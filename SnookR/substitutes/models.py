# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property


class Division(models.Model):
    '''
    A division must have a name and a division rep and can contain 0 or more teams and 0 or more subs
    Division -> Player  : 1 .. *
    Division -> Team    : 0 .. *
    Division -> Session : 1 .. *
    '''
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')

    division_rep = models.ForeignKey(User, related_name='division_representative')
    teams = models.ManyToManyField('teams.Team', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('division', args=[self.slug])


class Session(models.Model):
    '''
    Sessions are generally named after a season (summer, fall, etc), they have an associated game and
    division, as well as a start date and an end date.
    Session -> Division : 1 .. 1
    '''
    date_format = '%Y-%m-%d_%H-%M'
    pretty_date_format = '%x %H:%M'

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')

    game = models.CharField(max_length=100)
    division = models.ForeignKey(Division)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('session', args=self.get_url_args())

    def get_url_args(self):
        return [str(self.division.slug), str(self.slug)]

    def get_subs_with_unregister_urls(self):
        subs = self.subs.all()
        for sub in subs:
            sub.unregister_url = self.get_unregister_url(sub=sub)

        return subs

    def add_user_as_sub(self, user, date):
        sub = Sub.create_from_user(user, date)
        self.subs.add(sub)
        return self

    def remove_user_as_sub(self, user, date):
        sub = Sub.objects.get(user=user, date__date=date.date(), date__hour=date.hour, date__minute=date.minute)
        self.subs.remove(sub)
        return self


class SessionEvent(models.Model):
    start_time = models.TimeField()
    date = models.DateField()
    session = models.ForeignKey(Session)

    def __str__(self):
        return 'SessionEvent on {} for {}'.format(self.date, self.session)

    @property
    def get_register_url(self):
        return reverse('session-event-register', kwargs={'pk': self.id})

    @property
    def get_unregister_url(self):
        return reverse('session-event-unregister', kwargs={'pk': self.id})

    @property
    def get_absolute_url(self):
        kwargs = {'division': self.session.division.slug, 'session': self.session.slug, 'session_event': self.id}
        return reverse('session-event-detail', kwargs=kwargs)


class Sub(models.Model):
    '''
    Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
    willing to sub in a Division.

    Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
    Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
    session containing the dates of a particular session within a division. There are typically 3 sessions
    in a division per year, but the sessions don't necessarily correspond across divisions.
    '''
    user = models.ForeignKey('accounts.CustomUser')
    date = models.DateTimeField('sub date', auto_now=True)
    session_event = models.ForeignKey(SessionEvent)

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

    def is_registered(self, session_event: SessionEvent):
        return self.user.is_authenticated() and Sub.objects.filter(user=self.user, session_event=session_event).exists()
