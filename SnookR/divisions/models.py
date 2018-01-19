import calendar
from datetime import timedelta

from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models

from django.urls import reverse

from substitutes.models import Sub
from core import utils

class Division(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    division_rep = models.ForeignKey(User, related_name='represented_divisions_set')
    teams = models.ManyToManyField('teams.Team', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('divisions:division', args=[self.slug])


class Session(models.Model):
    date_format = '%Y-%m-%d_%H-%M'
    pretty_date_format = '%x %H:%M'
    division = models.ForeignKey(Division, related_name='session_set')
    name = models.CharField(max_length=200)
    game = models.CharField(max_length=100)
    start = models.DateField(null=False)
    end = models.DateField(null=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('divisions:session', args=self.get_url_args())

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


class SessionEventQuerySet(models.QuerySet):
    def create_repeated(self, session: Session, start_time, repeated='weekly', days=None):
        if days is None:
            days = []

        start = session.start
        end = session.end
        day_delta = timedelta(days=1)

        if repeated == 'weekly':
            multiplier = 7
        elif repeated == 'biweekly':
            multiplier = 14
        else:
            raise TypeError('argument "repeated" must be "weekly" or "biweekly", not {}'.format(repeated))

        print('ss', session.start, 'se', session.end)
        print('days', days)
        temp = start
        print('start', start)
        events = []
        for day in days:
            # Move temp up to first day
            while utils.lower_day_name[temp.weekday()] != day:
                temp += day_delta

            print('tmep start', temp)

            # Fill in days until the session's end
            while temp <= end:
                event = SessionEvent(date=temp, start_time=start_time, session=session)
                events.append(event)
                temp += (day_delta * multiplier)

            temp = start

        print(events)
        return SessionEvent.objects.bulk_create(events)


class SessionEvent(models.Model):
    start_time = models.TimeField()
    date = models.DateField(null=False)
    session = models.ForeignKey(Session, related_name='sessionevent_set')

    objects = SessionEventQuerySet.as_manager()

    def __str__(self):
        return 'SessionEvent on {} for {}'.format(self.date, self.session)

    @property
    def get_register_url(self):
        return reverse('divisions:session-event-register', kwargs={'pk': self.id})

    @property
    def get_unregister_url(self):
        return reverse('divisions:session-event-unregister', kwargs={'pk': self.id})

    @property
    def get_absolute_url(self):
        kwargs = {'division': self.session.division.slug, 'session': self.session.id, 'session_event': self.id}
        return reverse('divisions:session-event-detail', kwargs=kwargs)
