from autoslug import AutoSlugField
from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from django.urls import reverse

from substitutes.models import Sub


class Division(models.Model):
    '''
    A division must have a name and a division rep and can contain 0 or more teams and 0 or more subs
    Division -> Player  : 1 .. *
    Division -> Team    : 0 .. *
    Division -> Session : 1 .. *
    '''
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')

    division_rep = models.ForeignKey(User, related_name='represented_divisions_set')
    teams = models.ManyToManyField('teams.Team', blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('divisions:division', args=[self.slug])


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
    division = models.ForeignKey(Division, related_name='session_set')
    start_date = models.DateField('start date')
    end_date = models.DateField('end date')

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


class SessionEvent(models.Model):
    start_time = models.TimeField()
    date = models.DateField()
    session = models.ForeignKey(Session, related_name='sessionevent_set')

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
        kwargs = {'division': self.session.division.slug, 'session': self.session.slug, 'session_event': self.id}
        return reverse('divisions:session-event-detail', kwargs=kwargs)