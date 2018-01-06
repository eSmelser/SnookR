from django.db import models


class Message(models.Model):
    sender = models.ForeignKey('accounts.CustomUser', related_name='sender')
    receiver = models.ForeignKey('accounts.CustomUser', related_name='receiver')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, null=False)
