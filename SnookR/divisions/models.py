import calendar
from datetime import timedelta

from autoslug import AutoSlugField
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models

from django.urls import reverse
from django.utils.functional import cached_property

from substitutes.models import Sub
from core import utils
from teams.models import Team


class Division(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    division_rep = models.ForeignKey(User, related_name='divisions_set')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        content_type = ContentType.objects.get_for_model(Team)

        print('division id', self.id)
        codename = 'division.%s.add_team' % self.id
        name = 'Can add teams in division %s' % self.id
        print('codename', codename, 'name', name)
        permission = Permission.objects.create(
            codename=codename,
            name=name,
            content_type=content_type
        )
        group = Group.objects.create(name='division.%s.team_captain' % self.id)
        group.permissions.add(permission)

    @cached_property
    def add_team_permission(self):
        return Permission.objects.get(codename='division.%s.add_team' % self.id)

    @cached_property
    def team_captain_group(self):
        return Group.objects.get(name='division.%s.team_captain' % self.id)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('divisions:division', args=[self.slug])

    def make_captain(self, user):
        user.groups.add(self.team_captain_group)


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
        return reverse('divisions:session', kwargs={'division': self.division.id, 'session': self.id})

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


class DivRepRequest(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.OneToOneField('accounts.CustomUser', related_name='divreprequest')

    def __str__(self):
        return 'Div rep request for ' + str(self.user)
