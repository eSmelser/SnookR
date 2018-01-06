from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import SESSION_KEY
from django.urls import reverse
from django.core import mail
from accounts.views import signup
from accounts.models import CustomUser


class SignupTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.client = Client()
        self.data = {
            'username': 'joe',
            'password1': 'joepassword',
            'password2': 'joepassword',
            'email': 'joe@test.com',
            'first_name': 'joe',
            'last_name': 'pass'
        }

    def test_user_created(self):
        request = self.client.post(reverse('signup'), self.data)
        self.assertTrue(CustomUser.objects.all())

    def test_email_sent(self):
        request = self.client.post(reverse('signup'), self.data)
        self.assertEqual(len(mail.outbox), 1)
