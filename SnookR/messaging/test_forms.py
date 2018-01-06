from django.test import TestCase
from messaging.forms import MessageForm


class MessageFormTestCase(TestCase):
    def test_form_valid(self):
        data = { 'receiver': 1, 'sender': 2, 'text': 'Hey! foo bar.'}
        form = MessageForm(data)
        self.assertTrue(form.is_valid(), form.errors)
