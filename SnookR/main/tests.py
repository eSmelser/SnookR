import time
from django.test import LiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

class SeleniumTestCase(LiveServerTestCase):
    def setUp(self):
        super().setUp()
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)

    def tearDown(self):
        self.browser.quit()


class HomePageTestCase(SeleniumTestCase):
    def test_home_in_title(self):
        self.browser.get(self.live_server_url + '/home/')
        self.assertIn('Home', self.browser.title)

    def test_login_link(self):
        self.browser.get(self.live_server_url + '/home/')
        self.browser.find_element_by_id('login-link').click()
        self.assertIn('Login', self.browser.title)


class LoginPageTestCase(SeleniumTestCase):
    def test_login_fails_with_invalid_user(self):
        """Passes if invalid user login causes an 'errorlist' class to show"""
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys('John123')
        self.browser.find_element_by_id('id_password').send_keys('mypassword')
        self.browser.find_element_by_id('id_login_submit_button').click()

        passed = True
        try:
            self.browser.find_element_by_class_name('errorlist')
        except NoSuchElementException:
            passed = False

        self.assertTrue(passed)

    def test_login_passes_with_valid_user(self):
        """Passes if valid user login doesn't cause an 'errorlist' class to show"""
        # Valid username and password
        username = 'valid_username'
        password = 'valid_password'

        # Setup DB with user model instance
        user = User.objects.create_user(username=username, password=password)

        # Run test
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('id_login_submit_button').click()

        # Delete user from test DB because not needed now
        user.delete()

        # Check and assert pass/fail
        passed = False
        try:
            self.browser.find_element_by_class_name('errorlist')
        except NoSuchElementException:
            # If there is not an elem with errorlist class, this test passes
            passed = True

        self.assertTrue(passed)
