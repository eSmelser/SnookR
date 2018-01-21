from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import Permission
from django.utils import timezone

from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from substitutes.models import Sub
from divisions.models import Division, Session, SessionEvent
from accounts.models import User
from teams.models import Team
from invites.models import TeamInvite, SessionEventInvite
from api.serializers import SessionEventInvite
from messaging.models import Message

class UserListTestCase(APITestCase):
    def setUp(self):
        self.username = 'joe'
        self.password = 'joepassword'
        User.objects.create_user(username=self.username, password=self.password)

    def test_user_list(self):
        url = reverse('api:user_list')
        response = self.client.get(url)
        self.assertEqual(response.data[0]['username'], 'joe')

    def test_multiple_users_list(self):
        user = User.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        user.delete()

    def test_user_filter(self):
        user = User.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url, data={'username': 'myuser'}, format='json')
        self.assertEqual(len(response.data), 1)
        user.delete()

    def test_user_special_filter(self):
        user = User.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url, data={'username__icontains': 'my'}, format='json')
        self.assertEqual(len(response.data), 1)
        user.delete()


class TeamInviteTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee1 = User.objects.create_user(username='invitee1', password='invitee1password')
        self.invitee2 = User.objects.create_user(username='invitee2', password='invitee2password')

        self.team = Team.objects.create(captain=self.captain, name='My Team')
        self.invite1 = TeamInvite.objects.create(team=self.team, invitee=self.invitee1)
        self.invite2 = TeamInvite.objects.create(team=self.team, invitee=self.invitee2)
        self.client.login(username='captain', password='captainpassword')

    def test_invite_list(self):
        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)
        self.assertEqual(response.data[0]['team']['captain']['username'], self.captain.username)

    def test_invite_filtered_list(self):
        data = {'invitee__username': self.invitee2.username}
        url = reverse('api:invite_list')
        response = self.client.get(url, data=data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['invitee']['username'], self.invitee2.username)


class TeamInviteCreateTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = User.objects.create_user(username='invitee', password='inviteepassword')
        self.client.login(username='captain', password='captainpassword')
        self.team = Team.objects.create(captain=self.captain, name='My Team')

    def test_invite_create(self):
        url = reverse('api:team')
        team_data = self.client.get(url).data[0]

        data = {
            'team': team_data,
            'invitee': {'username': self.invitee.username},
        }

        url = reverse('api:invite_list')
        self.client.post(url, data, format='json')
        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)

        self.assertTrue(TeamInvite.objects.filter(invitee=self.invitee))
        self.assertEqual(response.data[0]['team']['captain']['username'], self.captain.username)


class TeamFilterTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = User.objects.create_user(username='invitee', password='inviteepassword')
        self.client.login(username='captain', password='captainpassword')
        self.team_name = 'My Team'
        self.team = Team.objects.create(captain=self.captain, name=self.team_name)
        self.team = Team.objects.create(captain=self.invitee, name=self.team_name)

    def test_basic_filter(self):
        url = reverse('api:team')
        data = {'id': self.team.id}
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 1)

        data['id'] = 99
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 0)

    def test_relational_filter(self):
        url = reverse('api:team')
        data = {'captain__id': self.captain.id}
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 1)

        data = {'captain__id': 99}
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 0)

        response = self.client.get(url, {}, format='json')
        self.assertEqual(len(response.data), 2)


class TeamPostTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

    def test_basic_post(self):
        url = reverse('api:team')
        data = {
            'name': 'My Team',
            'captain': {'username': self.captain.username},
            'players': [],
        }

        self.client.login(username='captain', password='captainpassword')
        self.client.post(url, data=data, format='json')
        self.assertTrue(Team.objects.filter(captain=self.captain))

    def test_basic_post_no_login(self):
        url = reverse('api:team')

        data = {
            'name': 'My Team',
            'captain': {'id': self.captain.id, 'username': self.captain.username,
                             'first_name': self.captain.first_name, 'last_name': self.captain.last_name},
            'players': [],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Team.objects.all())


class GetCurrentUserTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user', password='userpassword')
        self.client.login(username='user', password='userpassword')

    def test_get_current_user(self):
        url = reverse('api:user')
        response = self.client.get(url)
        self.assertEqual(response.data['username'], 'user')


class TeamInviteUpdateTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee1 = User.objects.create_user(username='invitee1', password='invitee1password')

        self.team = Team.objects.create(captain=self.captain, name='My Team')
        self.invite1 = TeamInvite.objects.create(team=self.team, invitee=self.invitee1)
        self.client.login(username='captain', password='captainpassword')

    def test_invite_list(self):
        self.client.login(username='invitee1', password='invitee1password')
        url = reverse('api:invite', kwargs={'pk': self.invite1.id})
        self.client.patch(url, data={'id': self.invite1.id, 'status': 'A'})
        obj = TeamInvite.objects.get(id=self.invite1.id)
        self.assertEqual(obj.status, 'A')


class UnregisteredPlayersTestCase(APITestCase):
    def setUp(self):
        self.captain = User.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)
        self.client.login(username='captain', password='captainpassword')
        self.team = Team.objects.create(captain=self.captain, name='myteam')

    def test_add_unregistered_player(self):
        url = reverse('api:unregistered_players')
        self.client.post(url, data={'name': 'jim', 'team': {'id': self.team.id}}, format='json')
        players = Team.objects.get(id=self.team.id).nonuserplayer_set.filter(name='jim')
        self.assertEquals(len(players), 1)


class SubListTestCase(APITestCase):
    def setUp(self):
        # Create divisions, sessions, users, and subs
        self.username = 'joe'
        self.password = 'joepassword'
        user = User.objects.create_user(username=self.username, password=self.password)
        division = Division.objects.create(name='Division A', division_rep=user)
        self.session = Session.objects.create(name='Session A', division=division, game='8ball',
                                              start_date=timezone.now(),
                                              end_date=timezone.now())

        self.session_event = SessionEvent.objects.create(
            start_time=self.session.start_date.time(),
            date=self.session.start_date.date(),
            session=self.session
        )

        self.add_user_to_session_as_sub(user)

    def test_request(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse('api:sub_list')
        response = self.client.get(url)
        json = response.json()
        self.assertEqual(json[0]['user']['username'], 'joe')

    def test_filter(self):
        user = User.objects.create_user(username='totally not joe', password=self.password)
        self.add_user_to_session_as_sub(user)

        self.client.login(username=self.username, password=self.password)
        url = reverse('api:sub_list')
        response = self.client.get(url, data={'user__username': 'joe'})
        json = response.json()
        self.assertEqual(json[0]['user']['username'], 'joe')
        self.assertEqual(len(json), 1)

    def add_user_to_session_as_sub(self, user):
        sub = Sub.objects.create(user=user, date=timezone.now(), session_event=self.session_event)

    def test_post(self):
        self.client.login(username=self.username, password=self.password)
        url = reverse('api:sub_list')
        data = { 'session_event': { 'id': self.session_event.id }, 'user': {'username': self.username}}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

class SessionEventTestCase(APITestCase):
    def setUp(self):
        self.username = 'joe'
        self.password = 'joepassword'
        user = User.objects.create_user(username=self.username, password=self.password)
        division = Division.objects.create(name='Division A', division_rep=user)

        self.now = datetime.now()
        start_time = datetime(self.now.year, self.now.month, self.now.day, self.now.hour)
        self.session = Session.objects.create(name='Session A', division=division, game='8ball',
                                              start_date=timezone.now(), end_date=timezone.now())
        SessionEvent.objects.create(session=self.session, start_time=start_time, date=self.now.date())
        SessionEvent.objects.create(session=self.session, start_time=start_time, date=self.now.date())

    def test_filter(self):

        url = reverse('api:session_events')
        json = self.client.get(url, data={'session__slug': self.session.slug}).json()
        self.assertEqual(json[0]['date'], str(self.now.date()))
        self.assertEqual(len(json), 2)

    def test_filter_empty(self):
        url = reverse('api:session_events')
        json = self.client.get(url, data={'session__slug': 'garbage'}).json()
        self.assertEqual(len(json), 0)


class SessionEventInviteTestCase(APITestCase):
    def setUp(self):
        self.username = 'joe'
        self.password = 'joepassword'
        self.user = User.objects.create_user(username=self.username, password=self.password)
        division = Division.objects.create(name='Division A', division_rep=self.user)

        self.now = datetime.now()
        start_time = datetime(self.now.year, self.now.month, self.now.day, self.now.hour)
        self.session = Session.objects.create(name='Session A', division=division, game='8ball',
                                              start_date=timezone.now(), end_date=timezone.now())

        self.session_event = SessionEvent.objects.create(session=self.session, start_time=start_time, date=self.now.date())
        self.sub = Sub.objects.create(user=self.user, date=timezone.now(), session_event=self.session_event)
        self.captain = User.objects.create_user(username='evan', password=self.password)

    def test_post(self):
        url = reverse('api:session_event_invite_list')
        response = self.client.post(url, { 'sub': {'id': self.sub.id, 'session_event': { 'id': self.sub.session_event.id }}, 'captain': {'username': self.captain.username } }, format='json')
        print(response.json())
        self.assertEqual(response.status_code, 201)


class MessageGetFilter(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='joe', password='password')
        self.user2 = User.objects.create_user(username='sue', password='password')
        self.messages = [Message.objects.create(text='text %s' % str(i), sender=self.user1, receiver=self.user2) for i in range(10)]

    def test_filter0(self):
        self.client.login(username=self.user1.username, password='password')
        url = reverse('api:message-list')
        response = self.client.get(url, data={'sender__username': self.user1.username})
        self.assertEqual(len(response.json()), len(self.messages))

    def test_filter1(self):
        self.client.login(username=self.user1.username, password='password')
        url = reverse('api:message-list')
        response = self.client.get(url, data={'sender__username': self.user2.username})
        self.assertEqual(len(response.json()), 0)

    def test_permission_denied(self):
        user3 = User.objects.create_user(username='jimmy', password='password')
        self.client.login(username=user3.username, password='password')
        url = reverse('api:message-list')
        response = self.client.get(url, data={'sender__username': self.user1.username})
        self.assertEqual(len(response.json()), 0)

    def test_list_order(self):
        """Passes if the return JSON is ordered by timestamp"""
        self.client.login(username=self.user1.username, password='password')
        url = reverse('api:message-list')
        response = self.client.get(url, data={'sender__username': self.user1.username})
        json = response.json()
        self.assertEqual(json[0]['id'], 1)
        self.assertEqual(json[-1]['id'], len(self.messages))

    def test_get_range(self):
        """Passes if the return JSON is ordered by timestamp"""
        self.client.login(username=self.user1.username, password='password')
        url = reverse('api:message-list')
        response = self.client.get(url, data={'id__gt': 1, 'id__lt': 5})
        json = response.json()
        self.assertEqual(len(json), 3)