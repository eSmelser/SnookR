from django.db import models
from django.db.models import Q


class MessageManager(models.Manager):
    def last_message_per_user(self, user):
        messages = self.all_related(user).order_by('-timestamp')

        pairs = []
        conversations = []
        for message in messages:
            users = {message.sender, message.receiver}
            if users not in pairs:
                conversations.append(message)
                pairs.append(users)

        return conversations

    def all_related(self, user):
        return self.select_related('sender', 'receiver').filter(Q(sender=user) | Q(receiver=user))


class Message(models.Model):
    sender = models.ForeignKey('accounts.CustomUser', related_name='sender')
    receiver = models.ForeignKey('accounts.CustomUser', related_name='receiver')
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now=True, null=False)

    objects = MessageManager()
