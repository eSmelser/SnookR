# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.utils import timezone

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from main.models import Team, Session, Sub, Division, UserProfile, CustomUser


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
        
        profiles = [
                    {
                        "phone_number": '123123123',
                        "user": user
                    }
                for user in users]

        self.stdout.write('Creating profiles...')
        _ = [UserProfile.objects.create(**profile) for profile in profiles]

        subs = [Sub.objects.create(user=user, date=timezone.now()) for user in users]

        divisions = [
                        {
                            "name": 'division_'+str(i),
                            "division_rep": user,
                        }
                    for i, user in enumerate(users)
        ]

        self.stdout.write('Creating divisions...')
        divisions = [Division.objects.create(**division) for division in divisions]

        sessions = [
                {
                    "name": 'session_'+str(i),
                    "game": str(i)+'ball',
                    "division": division,
                    "start_date": timezone.now(),
                    "end_date": timezone.now(),
                }
                for i, division in enumerate(divisions)]

        self.stdout.write('Creating sessions...')
        for session in sessions:
            s = Session.objects.create(**session)
            for sub in subs:
                s.subs.add(sub)

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