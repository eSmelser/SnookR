# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from autoslug import AutoSlugField
from sublist.models import Sublist

'''
A player can exist on many teams and in many divisions both as a division rep and/or as a sub, and these
are not mutually exlusive
Player -> Team     : 0 .. *
Player -> Division : 0 .. *
Player -> Sub      : 
'''


class Player(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        # chose not to use this because fName and lName are not required on users yet.
        #		name = self.user.first_name + ' ' + self.user.last_name
        return self.user.username

        # function to return all of the sublists related to a player instance

    def related_sublists(self):
        return Sublist.objects.filter(session__subs__player=self)

    def related_sessions(self):
        return Session.objects.filter(subs__player=self)


'''
Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
willing to sub in a Division. 

Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
session containing the dates of a particular session within a division. There are typically 3 sessions
in a division per year, but the sessions don't necessarily correspond across divisions.
'''


class Sub(models.Model):
    player = models.ForeignKey(Player)
    date = models.DateTimeField('sub date')

    def __str__(self):
        availability = self.player.user.username + ' is available ' + str(self.date)
        return availability


    def get_unregister_url(self):
        pass

    @property
    def sessions(self):
        return self.session_set.all()

    @staticmethod
    def create_from_user(user, date):
        player, _ = Player.objects.get_or_create(user=user)
        sub, _ = Sub.objects.get_or_create(player=player, date=date)
        return sub


'''
A team can contain many players but should only ever exist in one division
Team -> Player   : 1 .. *
Team -> Division : 1
'''


class Team(models.Model):
    name = models.CharField(max_length=200)
    #	division      = models.ForeignKey(Division, related_name="team's division")
    team_captain = models.ForeignKey(Player, related_name="team_captain")
    other_players = models.ManyToManyField(Player, blank=True)

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

    division_rep = models.ForeignKey(Player, related_name='division_representative')
    teams = models.ManyToManyField(Team, blank=True, related_name="divisions_teams")

    def __str__(self):
        return self.name


'''
Sessions are generally named after a season (summer, fall, etc), they have an associated game and
division, as well as a start date and an end date. 
Session -> Division : 1 .. 1
'''


class Session(models.Model):
    date_format = '%Y-%m-%d'

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
        sub = Sub.objects.get(player__user=user, date=date)
        self.subs.remove(sub)
        return self

    def user_is_registered(self, user):
        return self.subs.filter(player__user=user).exists()
