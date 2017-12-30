import time
from selenium import webdriver


class Driver():
    live_server_url = 'http://127.0.0.1:8000'

    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.implicitly_wait(3)
        self.team_name = 'MyTeam'
        self.data = {
            'evan': {
                'username': 'evan',
                'first_name': 'evan',
                'last_name': '',
                'password': 'evanpassword'
            },

            'bobby': {
                'username': 'bobby',
                'first_name': 'bobby',
                'last_name': '',
                'password': 'bobbypassword',
            }
        }


    def login(self, username, password):
        # Run test
        self.browser.get(self.live_server_url + '/login/')
        self.browser.find_element_by_id('id_username').send_keys(username)
        self.browser.find_element_by_id('id_password').send_keys(password)
        self.browser.find_element_by_id('id_submit_button').click()

    def invite_bobby(self):
        # 1. The team captain, evan, logs in.
        self.login(username=self.data['evan']['username'], password=self.data['evan']['password'])
        print('logged in')
        self.browser.find_element_by_id('id_teams_link').click()
        self.browser.find_element_by_id('id_add_team_link').click()
        self.browser.find_element_by_id('id_team_name').send_keys(self.team_name)
        self.browser.find_element_by_css_selector('#id_division > option:nth-child(1)').click()
        self.browser.find_element_by_id('id_search_player').send_keys(self.data['bobby']['username'])
        self.browser.find_element_by_id('id_add_button').click()
        self.browser.find_element_by_id('id_submit_button').click()

        # 2. evan creates a team with bobby on it and then logs out.
        time.sleep(.5)
        self.browser.find_element_by_id('id_logout_link').click()


if __name__ == '__main__':
    d = Driver()
    d.login(username=d.data['evan']['username'], password=d.data['evan']['password'])
    d.invite_bobby()