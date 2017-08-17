from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from main import models
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Populates database with default (test) data'

    def handle(self, *args, **options):
        users = [
                    {
                        "username"  : 'evan',
                        "password"  : 'evanpassword',
                        "first_name": 'evan',
                        "last_name" : 'smelser',
                        "email"     : 'e@sme.com',
                    },
                    {
                        "username"  : 'darrin',
                        "password"  : 'darrinpassword',
                        "first_name": 'darrin',
                        "last_name" : 'howard',
                        "email"     : 'darrin@test.com',
                    },
                    {
                        "username"  : 'jason',
                        "password"  : 'jasonpassword',
                        "first_name": 'jason',
                        "last_name" : 'bennett',
                        "email"     : 'jason@test.com',
                    },
                    {
                        "username"  : 'andy',
                        "password"  : 'andypassword',
                        "first_name": 'andy',
                        "last_name" : 'dalbey',
                        "email"     : 'andy@test.com',
                    },
                    {
                        "username"  : 'isaac',
                        "password"  : 'isaacpassword',
                        "first_name": 'isaac',
                        "last_name" : 'norman',
                        "email"     : 'isaac@test.com',
                    },
                    {
                        "username"  : 'chris',
                        "password"  : 'chrispassword',
                        "first_name": 'chris',
                        "last_name" : 'nieland',
                        "email"     : 'chris@test.com',
                    },
                    {
                        "username"  : 'sarah',
                        "password"  : 'sarahpassword',
                        "first_name": 'sarah',
                        "last_name" : 'nieland',
                        "email"     : 'sarah@test.com',
                    },
                    {
                        "username"  : 'nick',
                        "password"  : 'nickpassword',
                        "first_name": 'nick',
                        "last_name" : 'jordan',
                        "email"     : 'nick@test.com',
                    },
                    {
                        "username"  : 'pete',
                        "password"  : 'petepassword',
                        "first_name": 'pete',
                        "last_name" : 'gates',
                        "email"     : 'pete@test.com',
                    },
                ]
        users = [User.objects.create(**user) for user in users]
        
        
        players = [
                    {
                        "phone_number": '123123123',
                        "user": user
                    }
                for user in users]
        players = [models.Player.objects.create(**player) for player in players]

        subs = [models.Sub.objects.create(player=player, date=datetime.now()) for player in players]

        divisions = [
                        {
                            "name": 'division_'+str(i),
                            "division_rep": player,
                        }
                    for i, player in enumerate(players)]

        divisions = [models.Division.objects.create(**division) for division in divisions]

        sessions = [
                {
                    "name": 'session_'+str(i),
                    "game": str(i)+'ball',
                    "division": division,
                    "start_date": datetime.now(),
                    "end_date": datetime.now(),
                }
                for i, division in enumerate(divisions)]

        for session in sessions:
            s = models.Session.objects.create(**session)
            for sub in subs:
                s.subs.add(sub)
            



