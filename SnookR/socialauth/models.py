from django.db import models
from accounts.models import CustomUser, UserProfile


class FacebookAuthQuerySet(models.QuerySet):
    def get_or_create_user(self, first_name, last_name, email, facebook_id, image_url, phone_number, thumbnail):
        try:
            obj = self.get(facebook_id=facebook_id)
            created = False
        except FacebookAuth.DoesNotExist:
            username = CustomUser.unique_username(first_name, last_name)
            user = CustomUser.objects.create_user(username=username, first_name=first_name, last_name=last_name, email=email, password=facebook_id)
            profile = UserProfile.objects.create(user=user, image_url=image_url, phone_number=phone_number, thumbnail=thumbnail)
            profile.send_confirmation_email()
            obj = self.create(user=user, facebook_id=facebook_id)
            created = True

        return obj, created


class FacebookAuth(models.Model):
    user = models.ForeignKey('accounts.CustomUser', null=False)
    facebook_id = models.CharField(blank=False, max_length=32)

    objects = FacebookAuthQuerySet.as_manager()

    def __str__(self):
        return 'FacebookAuth: ' + str(self.user.username)