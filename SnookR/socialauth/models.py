import random


from django.db import models
from accounts.models import CustomUser, UserProfile



class FacebookAuthQuerySet(models.QuerySet):
    def create_user(self, first_name, last_name, email, facebook_id, image_url):
        username = CustomUser.unique_username(first_name, last_name)
        user = CustomUser.objects.create(username=username, first_name=first_name, last_name=last_name, email=email)
        profile = UserProfile.objects.create(user=user, image_url=image_url)
        profile.send_confirmation_email()
        return self.objects.create(user=user, facebook_id=facebook_id)


class FacebookAuth(models.Model):
    user = models.ForeignKey('accounts.CustomUser')
    facebook_id = models.CharField(blank=False, max_length=32)

    objects = FacebookAuthQuerySet.as_manager()

    def __str__(self):
        return 'FacebookAuth: ' + str(self.user.username)