from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from autoslug import AutoSlugField
from sublist.models import Sublist


class Player(models.Model):
    """
    A player can exist on many teams and in many divisions both as a division rep and/or as a sub, and these
    are not mutually exlusive
    Player -> Team     : 0 .. *
    Player -> Division : 0 .. *
    Player -> Sub      :
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.user.username

    def related_events(self):
        """Returns all of the events a player is subbing for."""
        sub = Sub.objects.get(player=self)
        return sub.location_set.filter(subs__in=[sub])

    #def related_sublists(self):
    #   """Returns all of the sublists related to a player instance"""
    #  return Sublist.objects.filter(session__subs__player=self)


class Team(models.Model):
    """
    A team can contain many players but should only ever exist in one division
    Team -> Player   : 1 .. *
    Team -> Division : 1
    """
    name = models.CharField(max_length=200)
    #	division      = models.ForeignKey(Division, related_name="team's division")
    team_captain = models.ForeignKey(Player, related_name="team_captain")
    other_players = models.ManyToManyField(Player, blank=True)

    def __str__(self):
        return self.name


class Division(models.Model):
    """
    A division must have a name and a division rep and can contain 0 or more teams and 0 or more subs
    Division -> Player  : 1 .. *
    Division -> Team    : 0 .. *
    Division -> Session : 1 .. *
    """

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name')
    division_rep = models.ForeignKey(Player, related_name='division_representative')
    teams = models.ManyToManyField(Team, blank=True, related_name="divisions_teams")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('division', kwargs={'division': self.slug})


class Session(models.Model):
    """
    Sessions are generally named after a season (summer, fall, etc), they have an associated game and
    division, as well as a start date and an end date.
    Session -> Division : 1 .. 1
    """

    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name')
    game = models.CharField(max_length=100)
    division = models.ForeignKey(Division)
    start_date = models.DateTimeField('start date')
    end_date = models.DateTimeField('end date')

    def __str__(self):
        return self.division.name + '_' + self.name + '_' + self.game

    def get_absolute_url(self):
        return reverse('session', kwargs={'session': str(self.slug), 'division': str(self.division.slug)})


class Sub(models.Model):
    """
    Subs are a "tuple-ish" construction tying a player and a date together to indicate what date they are
    willing to sub in a Division.

    Note: Eventually, I'd like players to be able to select a particular date that they could sub in a
    Division, OR, put themselves down for an entire session, in which case, we will likely need a model for
    session containing the dates of a particular session within a division. There are typically 3 sessions
    in a division per year, but the sessions don't necessarily correspond across divisions.
    """

    player = models.ForeignKey(Player)
    date = models.DateTimeField('sub date', auto_now=True)

    def __str__(self):
        availability = self.player.user.username + ' is available ' + str(self.date)
        return availability

    @property
    def sessions(self):
        return self.session_set.all()


class Location(models.Model):
    name = models.CharField(max_length=200)
    slug = AutoSlugField(populate_from='name')
    division = models.ForeignKey(Division)
    session = models.ForeignKey(Session)
    subs = models.ManyToManyField(Sub, blank=True)

    class Meta:
        unique_together = ('name', 'division', 'session')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(
            'location',
            kwargs={
                'division': str(self.division.slug),
                'session': str(self.session.slug),
                'location': str(self.slug)
            })

    def get_register_url(self):
        return reverse(
            'location_register',
            kwargs={
                'division': str(self.division.slug),
                'session': str(self.session.slug),
                'location': str(self.slug)
            })
