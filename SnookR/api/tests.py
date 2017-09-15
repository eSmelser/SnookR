from django.urls import reverse
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from main.models import Team, TeamInvite, CustomUser


class UserListTestCase(APITestCase):
    def setUp(self):
        self.username = 'joe'
        self.password = 'joepassword'
        CustomUser.objects.create_user(username=self.username, password=self.password)

    def test_user_list(self):
        url = reverse('api:user_list')
        response = self.client.get(url)
        self.assertEqual(response.data[0]['username'], 'joe')

    def test_multiple_users_list(self):
        user = CustomUser.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)
        user.delete()


class TeamInviteTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = CustomUser.objects.create_user(username='invitee', password='inviteepassword')
        self.team = Team.objects.create(team_captain=self.captain, name='My Team')
        self.invite = TeamInvite.objects.create(team=self.team, invitee=self.invitee)
        self.client.login(username='captain', password='captainpassword')

    def test_invite_list(self):
        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)
        self.assertEqual(response.data[0]['team']['team_captain'], self.captain.id)


class TeamInviteCreateTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = CustomUser.objects.create_user(username='invitee', password='inviteepassword')
        self.client.login(username='captain', password='captainpassword')
        self.team = Team.objects.create(team_captain=self.captain, name='My Team')

    def test_invite_create(self):
        url = reverse('api:team')
        team_data = self.client.get(url).data[0]

        data = {
            'team': team_data,
            'invitee': self.invitee.id,
        }

        url = reverse('api:invite_list')
        response = self.client.post(url, data, format='json')

        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)

        self.assertTrue(TeamInvite.objects.filter(invitee=self.invitee))
        self.assertEqual(response.data[0]['team']['team_captain'], self.captain.id)


class TeamFilterTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = CustomUser.objects.create_user(username='invitee', password='inviteepassword')
        self.client.login(username='captain', password='captainpassword')
        self.team_name = 'My Team'
        self.team = Team.objects.create(team_captain=self.captain, name=self.team_name)
        self.team = Team.objects.create(team_captain=self.invitee, name=self.team_name)


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
        data = {'team_captain__id': self.captain.id}
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 1)

        data = {'team_captain__id': 99}
        response = self.client.get(url, data, format='json')
        self.assertEqual(len(response.data), 0)

        response = self.client.get(url, {}, format='json')
        self.assertEqual(len(response.data), 2)
