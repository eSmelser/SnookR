from django.contrib.auth.models import Permission


from core.tests import SeleniumTestCase
from accounts.models import CustomUser
from teams.models import Team


class TeamInvitesTestCase(SeleniumTestCase):
    def setUp(self):
        super().setUp()
        permission = Permission.objects.get(codename='add_team')
        captain = CustomUser.objects.create_user(username='evan', password='password', first_name='evan', last_name='smelser')
        captain.user_permissions.add(permission)
        self.client.login(username='evan', password='password')
        self.user = CustomUser.objects.create_user(username='user', password='password', first_name='john', last_name='doe')

    def test_invitee_sees_accept_button(self):
        pass