from django.db import models
from django.contrib.auth.models import User


'''
A player can exist on many teams and in many divisions both as a division rep and/or as a sub, and these
are not mutually exlusive
Player -> Team     : 0 .. *
Player -> Division : 0 .. *
Player -> Sub      : 
'''
class Player(models.Model):
	username     = models.ForeignKey(User, related_name="players_username")
	first_name   = models.CharField(max_length=50)
	last_name    = models.CharField(max_length=50)
	phone_number = models.IntegerField(blank=True)
	email        = models.CharField(max_length=200, blank=True)

	def __str__(self):
		name = self.first_name + ' ' + self.last_name
		return name

	
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
	date   = models.DateTimeField('sub date')

	def __str__(self):
		return self.player + ' is available ' + self.date


'''
A team can contain many players but should only ever exist in one division
Team -> Player   : 1 .. *
Team -> Division : 1
'''
class Team(models.Model):
	name          = models.CharField(max_length=200)
#	division      = models.ForeignKey(Division, related_name="team's division")
	team_captain  = models.ForeignKey(Player, related_name="team_captain")
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
	name         = models.CharField(max_length=200)
	division_rep = models.ForeignKey(Player, related_name='division_representative')
	teams        = models.ManyToManyField(Team, blank=True, related_name="divisions_teams")
	subs         = models.ManyToManyField(Sub, blank=True, related_name="divisions_subs")

	def __str__(self):
		return self.name


'''
Sessions are generally named after a season (summer, fall, etc), they have an associated game and
division, as well as a start date and an end date. 
Session -> Division : 1 .. 1
'''
class Session(models.Model):
	name       = models.CharField(max_length=200)
	game       = models.CharField(max_length=100)
	division   = models.ForeignKey(Division)
	start_date = models.DateTimeField('start date')
	end_date   = models.DateTimeField('end date')



