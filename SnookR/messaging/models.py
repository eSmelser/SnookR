from django.db import models
from django.db.models import Q
from django.conf import settings


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

    def most_recent_friend_of(self, user):
        messages = self.last_message_per_user(user)
        if messages:
            return messages[0].get_not_user(user)


class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='receiver')
    sender_has_seen = models.BooleanField(default=False)
    receiver_has_seen = models.BooleanField(default=False)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, null=False)

    objects = MessageManager()

    def get_not_user(self, user):
        return {
            self.sender: self.receiver,
            self.receiver: self.sender
        }.get(user, None)