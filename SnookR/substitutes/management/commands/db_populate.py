# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING
import os
from datetime import datetime, timedelta

from django.utils import timezone
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from substitutes.models import Session, SessionEvent, Sub, Division
from accounts.models import CustomUser, UserProfile
from teams.models import Team
import random

TZINFO = timezone.get_current_timezone()
DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')


class Command(BaseCommand):
    help = 'Populates database with default (test) data'

    def handle(self, *args, **options):
        users = [
            {
                "username": 'evan',
                "password": 'evanpassword',
                "first_name": 'evan',
                "last_name": 'smelser',
                "email": 'e@sme.com',
            },
            {
                "username": 'darrin',
                "password": 'darrinpassword',
                "first_name": 'darrin',
                "last_name": 'howard',
                "email": 'darrin@test.com',
            },
            {
                "username": 'jason',
                "password": 'jasonpassword',
                "first_name": 'jason',
                "last_name": 'bennett',
                "email": 'jason@test.com',
            },
            {
                "username": 'andy',
                "password": 'andypassword',
                "first_name": 'andy',
                "last_name": 'dalbey',
                "email": 'andy@test.com',
            },
            {
                "username": 'isaac',
                "password": 'isaacpassword',
                "first_name": 'isaac',
                "last_name": 'norman',
                "email": 'isaac@test.com',
            },
            {
                "username": 'chris',
                "password": 'chrispassword',
                "first_name": 'chris',
                "last_name": 'nieland',
                "email": 'chris@test.com',
            },
            {
                "username": 'sarah',
                "password": 'sarahpassword',
                "first_name": 'sarah',
                "last_name": 'nieland',
                "email": 'sarah@test.com',
            },
            {
                "username": 'nick',
                "password": 'nickpassword',
                "first_name": 'nick',
                "last_name": 'jordan',
                "email": 'nick@test.com',
            },
            {
                "username": 'pete',
                "password": 'petepassword',
                "first_name": 'pete',
                "last_name": 'gates',
                "email": 'pete@test.com',
            },
        ]

        self.stdout.write('Creating users...')
        users = [CustomUser.objects.create_user(**user) for user in users]

        evan = users[0]
        content_type = ContentType.objects.get_for_model(Team)
        create_team_permission = Permission.objects.get(
            codename='add_team',
        )
        evan.user_permissions.add(create_team_permission)

        # Create admin
        admin = CustomUser.objects.create_user(username='admin', password='adminpassword')
        admin.is_superuser = True
        admin.is_staff = True
        admin.save()

        self.stdout.write('Creating profiles...')
        profiles = []
        for i, user in enumerate(users):
            profile = UserProfile.objects.create(user=user, phone_number='1231231234')
            name = 'profile_{}.jpeg'.format(i)
            with open(os.path.join(DATA_DIR, name), 'rb') as f:
                file = File(f)
                profile.thumbnail.save(name, file, save=True)

            profiles.append(profile)

        self.stdout.write('Creating divisions...')
        darrin = users[1]
        divisions = [
            Division.objects.create(name='Division A', division_rep=evan),
            Division.objects.create(name='Division B', division_rep=darrin)
        ]

        self.stdout.write('Creating sessions...')
        sessions = self.create_sessions(divisions)
        self.stdout.write('Creating session events...')
        for session in sessions:
            session_events = SessionEvent.objects.filter(session=session)
            for session_event in session_events:
                for user in users:
                    if random.random() < 0.1:
                        Sub.objects.create(user=user, date=timezone.now(), session_event=session_event)


        temp_users = users.copy()
        captain1 = temp_users.pop(0)
        captain2 = temp_users.pop(0)

        halfway = len(temp_users) // 2
        teams = [
            {
                'name': 'team 1',
                'team_captain': captain1,
                'players': temp_users[halfway:]
            },

            {
                'name': 'team 1',
                'team_captain': captain2,
                'players': temp_users[:halfway]
            },
        ]

        self.stdout.write('Creating teams...')

        temp = []
        for team in teams:
            players = team.pop('players')
            team = Team.objects.create(**team)
            team.players.add(*players)
            temp.append(team)

        teams = temp
        divisions[0].teams.add(teams[0])
        divisions[1].teams.add(teams[1])

    def create_sessions(self, divisions):
        session_names = ['wichita', '501 Bar', 'Location B', 'Rialto', 'SomeOtherSession', 'TheWhiteHouse', 'PSU',
                         'My House', 'Location Z']
        day = datetime(datetime.now().year, datetime.now().month, 1, tzinfo=TZINFO)
        session_divisions = []
        start_dates = []
        for i, _ in enumerate(session_names):
            day = day + timedelta(days=1)
            start_dates.append(day)
            if i < len(session_names) // 2:
                session_divisions.append(divisions[0])
            else:
                session_divisions.append(divisions[1])

        end_dates = [date + timedelta(hours=4) for date in start_dates]
        sessions = []
        for start, end, name, division in zip(start_dates, end_dates, session_names, session_divisions):
            session = Session.objects.create(name=name, game='8ball', division=division, start_date=start, end_date=end)
            sessions.append(session)

        for session in sessions:
            start = session.start_date
            start_hour = random.choice([16, 17, 18]) # Starts at 4, 5, or 6
            start_time = datetime(start.year, start.month, start.day, start_hour)

            # Make 8 weeks worth of events per session
            date = start.date()
            for _ in range(8):
                SessionEvent.objects.create(session=session, start_time=start_time, date=date)
                date += timedelta(days=7)

        return sessions