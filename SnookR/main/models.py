# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.db import models
from django.contrib.auth.models import User
from django.utils.functional import cached_property
from django.urls import reverse
from autoslug import AutoSlugField
from sublist.models import Sublist


class CustomUser(User):
    """This is a proxy model for the User model.  Proxy models just give methods
    to the base model, without creating any new tables"""

    class Meta:
        proxy = True

    def related_sublists(self):
        return Sublist.objects.filter(session__subs__user=self)

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
        return UserProfile.objects.get(user=self)

    @cached_property
    def sessions(self):
        return Session.objects.filter(subs__user=self)

    @cached_property
    def pending_invites(self):
        return TeamInvite.objects.filter(invitee=self, status=TeamInvite.PENDING)

    @cached_property
    def all_invites(self):
        return TeamInvite.objects.filter(invitee=self)

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
        # chose not to use this because fName and lName are not required on users yet.
        #		name = self.user.first_name + ' ' + self.user.last_name
        return self.user.username + "'s Profile"

        # function to return all of the sublists related to a player instance


'''
Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
willing to sub in a Division. 

Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
session containing the dates of a particular session within a division. There are typically 3 sessions
in a division per year, but the sessions don't necessarily correspond across divisions.
'''


class Sub(models.Model):
    user = models.ForeignKey(CustomUser)
    date = models.DateTimeField('sub date')

    def __str__(self):
        return self.date.strftime(Session.pretty_date_format)

    @cached_property
    def sessions(self):
        return self.session_set.all()

    @staticmethod
    def create_from_user(user, date):
        sub, _ = Sub.objects.get_or_create(user=user, date=date)
        return sub


'''
A team can contain many players but should only ever exist in one division
Team -> Player   : 1 .. *
Team -> Division : 1
'''


class Team(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team_captain = models.ForeignKey(CustomUser, related_name="team_captain")
    players = models.ManyToManyField(CustomUser, blank=True)

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


class NonUserPlayer(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')
    team = models.ForeignKey(Team)

    def __str__(self):
        return self.name


'''
A division must have a name and a division rep and can contain 0 or more teams and 0 or more subs
Division -> Player  : 1 .. *
Division -> Team    : 0 .. *
Division -> Session : 1 .. *
'''


class Division(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')

    division_rep = models.ForeignKey(User, related_name='division_representative')
    teams = models.ManyToManyField(Team, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('division', args=[self.slug])


'''
Sessions are generally named after a season (summer, fall, etc), they have an associated game and
division, as well as a start date and an end date. 
Session -> Division : 1 .. 1
'''


class Session(models.Model):
    date_format = '%Y-%m-%d_%H-%M'
    pretty_date_format = '%x %H:%M'

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name', always_update=True, default='')

    game = models.CharField(max_length=100)
    division = models.ForeignKey(Division)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')
    subs = models.ManyToManyField(Sub, blank=True)

    def __str__(self):
        return self.division.name + '_' + self.name + '_' + self.game

    def get_absolute_url(self):
        return reverse('session', args=self.get_url_args())

    def get_register_url(self):
        return reverse('session_register', args=self.get_url_args())

    def get_unregister_url(self, date):
        return reverse('session_unregister', args=self.get_url_args() + [date])

    def get_url_args(self):
        return [str(self.division.slug), str(self.slug)]

    def get_subs_with_unregister_urls(self):
        temp = []
        for sub in self.subs.all():
            datestring = sub.date.strftime(Session.date_format)
            sub.unregister_url = self.get_unregister_url(date=datestring)
            temp.append(sub)

        return temp

    def add_user_as_sub(self, user, date):
        sub = Sub.create_from_user(user, date)
        self.subs.add(sub)
        return self

    def remove_user_as_sub(self, user, date):
        sub = Sub.objects.get(user=user, date__date=date.date(), date__hour=date.hour, date__minute=date.minute)
        self.subs.remove(sub)
        return self

    def user_is_registered(self, user):
        return self.subs.filter(user=user).exists()


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
    invitee = models.ForeignKey(CustomUser)
    team = models.ForeignKey(Team)

    def __str__(self):
        return 'Invite from {} to {}'.format(self.team, self.invitee)

    @property
    def is_closed(self):
        return self.status != TeamInvite.PENDING