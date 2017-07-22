import time
from django.test import LiveServerTestCase, tag
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException


@tag('selenium')
class SeleniumTestCase(LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()


class HomePageTestCase(SeleniumTestCase):
    def test_home_in_title(self):
        """Passes if the home screen has 'Home' in the title."""
        self.browser.get(self.live_server_url + '/home/')
        self.assertIn('Home', self.browser.title)

    def test_login_link(self):
        """Passes if the login link goes to a screen with 'Login' in the title."""
        self.browser.get(self.live_server_url + '/home/')
        self.browser.find_element_by_id('login-link').click()
        self.assertIn('Login', self.browser.title)


class LoginPageTestCase(SeleniumTestCase):
    error_msg = 'Please enter a correct username and password'

    def test_login_fails_with_invalid_user(self):
        """Passes if an invalid user login displays an error prompt.

        The user goes to the login screen and types in an invalid username
        and password, and then clicks on the submit button.  The page shows an
        error saying: 'Please enter a correct username and password'.
        """
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys('John123')
        self.browser.find_element_by_id('id_password').send_keys('mypassword')
        self.browser.find_element_by_id('id_submit_button').click()

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
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('id_submit_button').click()

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

        # Check preconditions
        user = User.objects.filter(username=username)
        self.assertEqual(len(user), 0)

        # Run test
        self.browser.get(self.live_server_url + '/signup/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password1').send_keys(password)
        self.browser.find_element_by_id('id_password2').send_keys(password)
        self.browser.find_element_by_id('id_submit_button').click()

        # Check that the DB now has one user with username == username
        user = User.objects.filter(username=username)
        self.assertEqual(len(user), 1)
