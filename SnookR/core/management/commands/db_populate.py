# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING
import os
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.files import File
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from substitutes.models import Sub
from divisions.models import Division, Session, SessionEvent
from accounts.models import UserProfile
from teams.models import Team, Captain
import random

User = get_user_model()

TZINFO = timezone.get_current_timezone()
DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data')

USERS = [
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


class Command(BaseCommand):
    help = 'Populates database with default (test) data'

    def handle(self, *args, **options):
        self.stdout.write('Creating users...')

        users = []
        for i, user in enumerate(USERS):
            obj = User.objects.create_user(**user)
            users.append(obj)

        evan = users[0]
        create_team_permission = Permission.objects.get(
            codename='add_team',
        )
        evan.user_permissions.add(create_team_permission)

        perm = Permission.objects.get(
            codename='add_division',
        )
        evan.user_permissions.add(perm)

        User.objects.create_superuser(username='admin', password='adminpassword', email='admin@test.com')

        self.stdout.write('Creating profiles...')
        profiles = []
        for i, user in enumerate(users):
            profile, created = UserProfile.objects.get_or_create(user=user, phone_number='1231231234')
            name = 'profile_{}.jpeg'.format(i)
            with open(os.path.join(DATA_DIR, name), 'rb') as f:
                file = File(f)
                profile.thumbnail.save(name, file, save=True)
            profile.save()
            profiles.append(profile)

        self.stdout.write('Creating divisions...')
        darrin = users[1]
        divisions = [
            Division.objects.create(name='Division A', representative=evan),
            Division.objects.create(name='Division B', representative=darrin)
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

        self.stdout.write('Creating teams...')
        temp_users = users.copy()
        evan = temp_users.pop(0)
        darrin = temp_users.pop(0)
        division1 = divisions[0]
        division2 = divisions[1]

        captain1 = Captain.objects.create(user=evan, division=division1)
        captain2 = Captain.objects.create(user=darrin, division=division2)

        halfway = len(temp_users) // 2
        first_half = temp_users[halfway:]
        second_half = temp_users[:halfway]
        t1 = Team.objects.create(name='team 1', captain=captain1)
        t2 = Team.objects.create(name='team 2', captain=captain2)
        t1.players.add(*first_half)
        t2.players.add(*second_half)

    def create_sessions(self, divisions):
        names = [
            'wichita',
            '501 Bar',
            'Location B',
            'Rialto',
            'SomeOtherSession',
            'TheWhiteHouse',
            'PSU',
            'My House',
            'Location Z'
        ]
        day = datetime(datetime.now().year, datetime.now().month, 1, tzinfo=TZINFO)
        session_divisions = []
        start_dates = []
        for i, _ in enumerate(names):
            day = day + timedelta(days=1)
            start_dates.append(day)
            if i < len(names) // 2:
                session_divisions.append(divisions[0])
            else:
                session_divisions.append(divisions[1])

        end_dates = [date + timedelta(days=30 * 3) for date in start_dates]
        sessions = []
        for start, end, name, division in zip(start_dates, end_dates, names, session_divisions):
            session = Session.objects.create(name=name, game='8ball', division=division, start=start,
                                             end=end)
            sessions.append(session)

        for session in sessions:
            start = session.start
            start_hour = random.choice([16, 17, 18])  # 4pm, 5pm, or 6pm
            start_time = datetime(start.year, start.month, start.day, start_hour)

            # Make 8 weeks worth of events per session
            date = start.date()
            for _ in range(8):
                SessionEvent.objects.create(session=session, start_time=start_time, date=date)
                date += timedelta(days=7)

        return sessions
