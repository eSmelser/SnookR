from django.conf import settings
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag

from selenium import webdriver


@tag('selenium')
class SeleniumTestCase(StaticLiveServerTestCase):
    def setUp(self):
        super().setUp()
        if settings.CHROME_DRIVER:
            self.browser = webdriver.Chrome(settings.CHROME_DRIVER)
        else:
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