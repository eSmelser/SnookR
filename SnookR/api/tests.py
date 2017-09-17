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

    def test_user_filter(self):
        user = CustomUser.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url, data={'username': 'myuser'}, format='json')
        self.assertEqual(len(response.data), 1)
        user.delete()

    def test_user_special_filter(self):
        user = CustomUser.objects.create_user(username='myuser', password='password')
        url = reverse('api:user_list')
        response = self.client.get(url, data={'username__icontains': 'my'}, format='json')
        self.assertEqual(len(response.data), 1)
        user.delete()


class TeamInviteTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee1 = CustomUser.objects.create_user(username='invitee1', password='invitee1password')
        self.invitee2 = CustomUser.objects.create_user(username='invitee2', password='invitee2password')

        self.team = Team.objects.create(team_captain=self.captain, name='My Team')
        self.invite1 = TeamInvite.objects.create(team=self.team, invitee=self.invitee1)
        self.invite2 = TeamInvite.objects.create(team=self.team, invitee=self.invitee2)
        self.client.login(username='captain', password='captainpassword')

    def test_invite_list(self):
        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)
        self.assertEqual(response.data[0]['team']['team_captain']['username'], self.captain.username)

    def test_invite_filtered_list(self):
        data = {'invitee__username': self.invitee2.username}
        url = reverse('api:invite_list')
        response = self.client.get(url, data=data)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['invitee']['username'], self.invitee2.username)


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
            'invitee': {'username': self.invitee.username },
        }

        url = reverse('api:invite_list')
        self.client.post(url, data, format='json')
        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('api:invite_list')
        response = self.client.get(url)

        self.assertTrue(TeamInvite.objects.filter(invitee=self.invitee))
        self.assertEqual(response.data[0]['team']['team_captain']['username'], self.captain.username)


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


class TeamPostTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

    def test_basic_post(self):
        url = reverse('api:team')
        data = {
            'name': 'My Team',
            'team_captain': {'username': self.captain.username},
            'players': [],
        }

        self.client.login(username='captain', password='captainpassword')
        self.client.post(url, data=data, format='json')
        self.assertTrue(Team.objects.filter(team_captain=self.captain))

    def test_basic_post_no_login(self):
        url = reverse('api:team')

        data = {
            'name': 'My Team',
            'team_captain': {'id': self.captain.id, 'username': self.captain.username, 'first_name': self.captain.first_name, 'last_name': self.captain.last_name},
            'players': [],
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Team.objects.all())


class GetCurrentUserTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username='user', password='userpassword')
        self.client.login(username='user', password='userpassword')

    def test_get_current_user(self):
        url = reverse('api:user')
        response = self.client.get(url)
        self.assertEqual(response.data['username'], 'user')