from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import SESSION_KEY
from django.urls import reverse
from django.core import mail
from accounts.views import signup
from accounts.models import User


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
        self.assertTrue(User.objects.all())

    def test_email_sent(self):
        request = self.client.post(reverse('signup'), self.data)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_content(self):
        request = self.client.post(reverse('signup'), self.data)
        user = User.objects.get(username=self.data['username'])
        email = mail.outbox.pop()
        self.assertIn(user.username, email.body)
        self.assertIn(user.first_name, email.body)
        self.assertIn(user.profile.activation_key, email.body)
        self.assertIn(str(user.profile.key_expires), email.body)
