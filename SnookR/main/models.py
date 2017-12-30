# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

import functools
from autoslug import AutoSlugField
from django.contrib.auth.models import User, UserManager
from django.db.models import Q
from django.db import models
from django.urls import reverse
from django.utils.functional import cached_property
from rest_framework.renderers import JSONRenderer

from api import serializers


class CustomUserQuerySet(models.QuerySet):
    def search(self, string):
        query = Q()
        for term in string.split():
            query |= Q(username__startswith=term) | Q(first_name__startswith=term) | Q(last_name__startswith=term)

        return self.filter(query)


class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    def search(self, string):
        return self.get_queryset().search(string)


class CustomUser(User):
    """This is a proxy model for the User model.  Proxy models just give methods
    to the base model, without creating any new tables"""

    class Meta:
        proxy = True

    objects = CustomUserManager()

    def as_json(self):
        return {
            'userName': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'id': self.id,
            'url': self.get_absolute_url,
        }

    @cached_property
    def profile(self):
        try:
            return UserProfile.objects.get(user=self)
        except UserProfile.DoesNotExist:
            return None

    @cached_property
    def sessions(self):
        return Session.objects.filter(subs__user=self)

    @cached_property
    def pending_invites(self):
        return self.teaminvite_set.filter(invitee=self, status='P')

    @cached_property
    def all_invites(self):
        return self.teaminvite_set.filter(invitee=self)

    @staticmethod
    def from_user(user):
        return CustomUser.objects.get(id=user.id)

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

'''
A player can exist on many teams and in many divisions both as a division rep and/or as a sub, and these
are not mutually exlusive
Player -> Team     : 0 .. *
Player -> Division : 0 .. *
Player -> Sub      : 
'''


def thumbnail_path(instance, filename):
    return 'uploads/user/{0}/{1}'.format(instance.user.username, filename)


class UserProfile(models.Model):
    """User profiles are used to extend the User model with more fields, but not to change
    the User model.  Sometimes altered user models conflict with other third-party apps, and
    this is the most conflict-free way to extend the User model."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.IntegerField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=thumbnail_path, null=True)

    def __str__(self):
        return self.user.username + "'s Profile"

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})


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

    def get_register_url(self):
        return reverse('session_register', args=self.get_url_args())

    def get_unregister_url(self, sub):
        datestring = sub.date.strftime(Session.date_format)
        return reverse('session_unregister', args=self.get_url_args() + [datestring])

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
        return reverse('session_event_register', kwargs={'pk': self.id})

    @property
    def get_unregister_url(self):
        return reverse('session_event_unregister', kwargs={'pk': self.id})

    def as_json(self):
        serializer = serializers.SessionEventSerializer(self)
        return JSONRenderer().render(serializer.data)

    @property
    def get_absolute_url(self):
        kwargs = {'division': self.session.division.slug, 'session': self.session.slug}
        return reverse('session', kwargs=kwargs) + '?sessionEventId=' + str(self.id)


class Sub(models.Model):
    '''
    Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
    willing to sub in a Division. 

    Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
    Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
    session containing the dates of a particular session within a division. There are typically 3 sessions
    in a division per year, but the sessions don't necessarily correspond across divisions.
    '''
    user = models.ForeignKey(CustomUser)
    date = models.DateTimeField('sub date', auto_now=True)
    session_event = models.ForeignKey(SessionEvent)

    def __str__(self):
        return str(self.user)

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
