import random
from datetime import timedelta
from django.contrib.auth.models import UserManager, User
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone

from substitutes.models import Session
import random


def thumbnail_path(instance, filename):
    return 'uploads/user/{0}/{1}'.format(instance.user.username, filename)


class CustomUserQuerySet(models.QuerySet):
    def search(self, string):
        query = Q()
        for term in string.split():
            query |= Q(username__startswith=term) | Q(first_name__startswith=term) | Q(last_name__startswith=term)

        print('string', string)
        return self.filter(query)


class CustomUserManager(UserManager):
    def get_queryset(self):
        return CustomUserQuerySet(self.model, using=self._db)

    def search(self, string):
        return self.get_queryset().search(string)


class CustomUser(User):
    """This is a proxy model for the User model.  Proxy models just give methods
    to the base model, without creating any new tables"""

    class Meta:
        proxy = True

    objects = CustomUserManager()

    def as_json(self):
        return {
            'userName': self.username,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'id': self.id,
            'url': self.get_absolute_url,
        }

    @cached_property
    def profile(self):
        try:
            return UserProfile.objects.get(user=self)
        except UserProfile.DoesNotExist:
            return None

    @cached_property
    def sessions(self):
        return Session.objects.filter(subs__user=self)

    @cached_property
    def pending_invites(self):
        return self.teaminvite_set.filter(invitee=self, status='P')

    @cached_property
    def all_invites(self):
        return self.teaminvite_set.filter(invitee=self)

    @staticmethod
    def from_user(user):
        return CustomUser.objects.get(id=user.id)

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

    @cached_property
    def full_name(self):
        return str(self.first_name) + ' ' + str(self.last_name)


def generate_expiration():
    return timezone.now() + timedelta(minutes=20)


def generate_key():
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


class UserProfile(models.Model):
    """User profiles are used to extend the User model with more fields, but not to change
    the User model.  Sometimes altered user models conflict with other third-party apps, and
    this is the most conflict-free way to extend the User model."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.IntegerField(blank=True, null=True)
    thumbnail = models.ImageField(upload_to=thumbnail_path, null=True)
    activation_key = models.CharField(max_length=6, default=generate_key)
    key_expires = models.DateTimeField(default=generate_expiration)

    def __str__(self):
        return self.user.username + "'s Profile"

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})

    def reset_key(self):
        self.activation_key = generate_key()
        self.key_expires = generate_expiration()
        self.save()
