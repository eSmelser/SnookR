# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

import time
from django.test import tag
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import Permission, User
from django.contrib.contenttypes.models import ContentType
from main.models import CustomUser, Team, Division, TeamInvite
from selenium import webdriver


@tag('selenium')
class SeleniumTestCase(StaticLiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()

    def login(self, username, password):
        # Run test
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('id_submit_button').click()


class NavbarTestCase(SeleniumTestCase):
    def test_navbar_shows_login_if_user_not_authenticated(self):
        """Passes if the navbar shows a login link for unauthenticated users"""
        self.browser.get(self.live_server_url + '/home/')
        self.assertIn('Login', self.browser.page_source)

    def test_navbar_shows_logout_if_user_is_authenticated(self):
        """Passes if the navbar shows a logout link for authenticated users"""
        # Valid username and password
        username = 'valid_username'
        password = 'valid_password'

        # Setup DB with user model instance
        user = User.objects.create_user(username=username, password=password)

        # Login user
        self.login(username, password)

        # Run Test
        self.browser.get(self.live_server_url + '/home/')
        navbar = self.browser.find_element_by_class_name('navbar')
        self.assertIn('Logout', navbar.text)
        self.assertNotIn('Login', navbar.text)
        self.assertNotIn('Signup', navbar.text)

    def test_authenticated_navbar_shows_username(self):
        """Passes if authenticated user shows username in navbar.

        The user (username is JohnDoe) logs in as JohnDoe, he sees in the
        navbar 'Signed in as JohnDoe'.
        """
        username = 'JohnDoe'
        password = 'mycoolpassword'

        # Setup DB with user model instance and login
        user = User.objects.create_user(username=username, password=password)
        self.browser.get(self.live_server_url + '/login/')
        self.login(username, password)
        self.browser.get(self.live_server_url + '/home/')

        # Assert that the message is in the navbar
        expected = 'Signed in as JohnDoe'
        navbar = self.browser.find_element_by_class_name('navbar')
        self.assertIn(expected, navbar.text)

        # Clean up
        user.delete()


class HomePageTestCase(SeleniumTestCase):
    def test_home_in_title(self):
        """Passes if the home screen has 'Home' in the title."""
        self.browser.get(self.live_server_url + '/home/')
        self.assertIn('Home', self.browser.title)

    def test_login_link(self):
        """Passes if the login link goes to a screen with 'Login' in the title."""
        self.browser.get(self.live_server_url + '/home/')
        self.browser.find_element_by_id('id_login_link').click()
        self.assertIn('Login', self.browser.title)


class LoginPageTestCase(SeleniumTestCase):
    error_msg = 'Please enter a correct username and password'

    def test_login_fails_with_invalid_user(self):
        """Passes if an invalid user login displays an error prompt.

        The user goes to the login screen and types in an invalid username
        and password, and then clicks on the submit button.  The page shows an
        error saying: 'Please enter a correct username and password'.
        """
        self.login(username='John123', password='mypassword')

        elem = self.browser.find_element_by_class_name('errorlist')
        self.assertIn(self.error_msg, elem.text)

    def test_login_passes_with_valid_user(self):
        """Passes if valid user login doesn't cause an error prompt to show.

        The user goes to the login screen and types in a valid username
        and password, and then clicks on the submit button.  The page redirects
        successfully with on error.
        """
        # Valid username and password
        username = 'valid_username'
        password = 'valid_password'

        # Setup DB with user model instance
        user = User.objects.create_user(username=username, password=password)

        # Run test
        self.login(username, password)

        # Delete user from test DB because not needed now
        user.delete()

        # Check and assert pass/fail
        self.assertNotIn(self.error_msg, self.browser.page_source)


class SignupPageTestCase(SeleniumTestCase):
    def test_signup_adds_user(self):
        """Passes if filling out the signup form creates a new user.

        The user goes to the signup page and types in their username, password,
        and confirmation password.  They click the submit button.  Their
        gets stored in the user database.
        """
        username = 'JohnDoe'
        password = 'mycoolpassword'
        email = 'jd@gmail.com'
        # Check preconditions
        user = User.objects.filter(username=username)
        self.assertEqual(len(user), 0)

        # Run test
        self.browser.get(self.live_server_url + '/signup/')
        self.browser.find_element_by_id('id_username').send_keys(username)

        self.browser.find_element_by_id('id_email').send_keys(email)
        self.browser.find_element_by_id('id_password1').send_keys(password)
        self.browser.find_element_by_id('id_password2').send_keys(password)
        self.browser.find_element_by_id('id_submit_button').click()

        # Check that the DB now has one user with username == username
        users = User.objects.filter(username=username)
        user_count = len(users)
        users.delete()
        self.assertEqual(user_count, 1)


class TeamInviteTestCase(SeleniumTestCase):
    def setUp(self):
        super().setUp()
        """Setup the test db.

        1. Populate the database with two players: one team captain and one regular player

        """
        self.team_name = 'MyTeam'
        self.data = {
            'joe': {
                'username': 'joe',
                'first_name': 'joe',
                'last_name': 'smith',
                'password': 'joepassword'
            },

            'will': {
                'username': 'will',
                'first_name': 'will',
                'last_name': 'bacci',
                'password': 'willpassword',
            }
        }
        joe = CustomUser.objects.create_user(**self.data['joe'])
        content_type = ContentType.objects.get_for_model(Team)
        permission = Permission.objects.get(
            codename='add_team',
            content_type=content_type,
        )
        joe.user_permissions.add(permission)
        CustomUser.objects.create_user(**self.data['will'])

        rep = CustomUser.objects.create_user(username='rep', password='reppassword')
        Division.objects.create(name='division 1', division_rep=rep)

    def joe_invite_will(self):
        # 1. The team captain, Joe, logs in.
        self.login(username=self.data['joe']['username'], password=self.data['joe']['password'])

        self.browser.find_element_by_id('id_teams_link').click()
        self.browser.find_element_by_id('id_add_team_link').click()
        self.browser.find_element_by_id('id_team_name').send_keys(self.team_name)
        self.browser.find_element_by_css_selector('#id_division > option:nth-child(1)').click()
        self.browser.find_element_by_id('id_search_player').send_keys(self.data['will']['username'])
        self.browser.find_element_by_id('id_add_button').click()
        self.browser.find_element_by_id('id_submit_button').click()

        # 2. Joe creates a team with Will on it and then logs out.
        time.sleep(.5)
        self.browser.find_element_by_id('id_logout_link').click()

    def test_create_team_causes_invite(self):
        """Passes if a user can see a new request number on his navbar after being added on a team."""

        # 1. The team captain, Joe, logs in.
        # 2. Joe creates a team with Will on it and then logs out.
        self.joe_invite_will()

        # 3. Will logs in and sees that his Invites navbar button now has a number 1 badge next to it
        #    to indicate a new invite
        self.login(username=self.data['will']['username'], password=self.data['will']['password'])

        # Assertion: The invite text displays 1
        text = self.browser.find_element_by_id('id_invites_badge').text
        self.assertIn('1', text)

    def test_will_sees_invite_list(self):
        self.joe_invite_will()
        self.login(username=self.data['will']['username'], password=self.data['will']['password'])
        self.browser.find_element_by_id('id_invites_link').click()
        text = self.browser.find_element_by_id('id_pending_invites_list').text
        self.assertIn(self.team_name, text)
        self.assertIn(self.data['joe']['username'], text)

    def test_will_accepts_invite(self):
        self.joe_invite_will()
        self.login(username=self.data['will']['username'], password=self.data['will']['password'])
        self.browser.find_element_by_id('id_invites_link').click()
        id = TeamInvite.objects.all()[0].id
        self.browser.find_element_by_id('id_accept_button_' + str(id)).click()
        text = self.browser.find_element_by_id('id_accepted_invites_list').text
        self.assertIn('joe', text)
        obj = TeamInvite.objects.get(invitee__username='will', team__team_captain__username='joe')
        self.assertEqual(obj.status, TeamInvite.APPROVED)


class AccountTestCase(SeleniumTestCase):
    def setUp(self):
        super().setUp()
        self.username = 'user'
        self.password = 'userpassword'
        self.email = 'user@gmail.com'

        user = CustomUser.objects.create_user(username=self.username, password=self.password)
        self.old_hashed_pass = user.password
        self.login(username=self.username, password=self.password)

    def test_account_delete(self):
        self.browser.find_element_by_id("id_account_link").click()
        self.browser.find_element_by_id("id_delete_account_link").click()
        self.browser.find_element_by_id("id_delete_account_confirm_link").click()
        self.assertIn('Deleted', self.browser.find_element_by_id('id_confirmation_message').text)
        self.assertTrue(not CustomUser.objects.all().exists())

    def test_change_password(self):
        self.browser.find_element_by_id("id_account_link").click()
        self.browser.find_element_by_id("id_password_change_link").click()
        new_password = 'mynewpassword'
        self.browser.find_element_by_id("id_old_password").send_keys(self.password)
        self.browser.find_element_by_id('id_new_password1').send_keys(new_password)
        self.browser.find_element_by_id('id_new_password2').send_keys(new_password)
        self.browser.find_element_by_id('id_submit_button').click()
        self.browser.find_element_by_id('id_logout_link').click()

        new_hashed_pass = CustomUser.objects.get(username=self.username).password
        self.assertNotEqual(self.old_hashed_pass, new_hashed_pass)
        self.login(username=self.username, password=new_password)
        nav_text = self.browser.find_element_by_css_selector('nav').text
        self.assertIn(self.username, nav_text)