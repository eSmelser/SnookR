from django.urls import reverse
from django.contrib.auth.models import Permission
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase
from main.models import Team, TeamInvite, CustomUser

class TeamInviteTestCase(APITestCase):
    def setUp(self):
        self.captain = CustomUser.objects.create_user(username='captain', password='captainpassword')
        permission = Permission.objects.get(codename='add_team')
        self.captain.user_permissions.add(permission)

        self.invitee = CustomUser.objects.create_user(username='invitee', password='inviteepassword')
        self.client.login(username='captain', password='captainpassword')


    def test_invite_create(self):
        data = {
            'teamName': 'My Team',
            'players': [self.invitee.as_json()],
            'unregisteredPlayers': [],
        }
        url = reverse('team_create')
        response = self.client.post(url, data, format='json')

        self.client.login(username='invitee', password='inviteepassword')
        url = reverse('invite_list')
        response = self.client.get(url)

        self.assertTrue(TeamInvite.objects.filter(invitee=self.invitee))
        self.assertEqual(response.data[0]['team']['team_captain'], self.captain.id)