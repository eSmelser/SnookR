import random
from datetime import timedelta

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.staticfiles.templatetags.staticfiles import static

from divisions.models import Division, Session
from invites.models import TeamInvite, SessionEventInvite
from teams.models import Team


def thumbnail_path(instance, filename):
    """Returns the path in which to save an uploaded thumbnail image"""
    return 'uploads/user/{0}/{1}'.format(instance.user.username, filename)


def generate_expiration():
    """Returns an datetime in which a new user confirmation key will expire."""
    return timezone.now() + timedelta(minutes=20)


def generate_key():
    """Returns a new user confirmation key."""
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


class CustomUserManager(UserManager):
    def search(self, string):
        """Returns a queryset of users with usernames, first names, or last names that start with any word 
        in string.
        
        Parameters:
            string: str
                A string of one or more words separated by whitespace.
        
        """
        query = Q()
        for term in string.split():
            query |= Q(username__startswith=term) | Q(first_name__startswith=term) | Q(last_name__startswith=term)

        return self.get_queryset().filter(query)


class User(AbstractUser):
    objects = CustomUserManager()

    @cached_property
    def profile(self):
        try:
            return UserProfile.objects.get(user=self)
        except UserProfile.DoesNotExist:
            return None

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

    @property
    def invites_count(self):
        return SessionEventInvite.objects.filter(
            sub__user=self).pending().count() + self.teaminvite_set.pending().count()

    def is_division_rep(self):
        return self.represented_divisions_set.all().exists()

    def is_captain(self):
        return self.is_authenticated() and self.captain_divisions.exists()

    @cached_property
    def captain_divisions(self):
        query = Q(name__startswith='division') & Q(name__endswith='team_captain')
        groups = self.groups.filter(query)
        ids = []
        for group in groups:
            name = group.name
            id_ = name.lstrip('division.').rstrip('.team_captain')  # 'division.2.team_captain' -> '2'
            id_ = int(id_)
            ids.append(id_)

        return Division.objects.filter(pk__in=ids)


class UserProfile(models.Model):
    """User profiles are used to extend the User model with more fields, but not to change
    the User model.  Sometimes altered user models conflict with other third-party apps, and
    this is the most conflict-free way to extend the User model."""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
    )
    phone_number = models.CharField(blank=True, null=True, max_length=20)
    thumbnail = models.ImageField(upload_to=thumbnail_path, null=True, blank=True)
    activation_key = models.CharField(max_length=6, default=generate_key)
    key_expires = models.DateTimeField(default=generate_expiration)
    image_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.user.username + "'s Profile"

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.user.username})

    def reset_key(self):
        self.activation_key = generate_key()
        self.key_expires = generate_expiration()
        self.save()

    @property
    def thumbnail_url(self):
        """Returns user's thumbnail url.

        Uploaded image takes precedence, followed by any image url saved (e.g, from social auth), followed by the
        placeholder.
        """
        if self.thumbnail:
            return self.thumbnail.url
        elif self.image_url:
            return self.image_url
        else:
            return static('divisions/images/default_profile.jpg')

    def send_confirmation_email(self):
        activation_key = self.activation_key
        key_expires = self.key_expires
        dummy_message = '{} {} {} {}'.format(self.user.first_name, self.user.username, activation_key, key_expires)
        send_mail(
            'Subject here',
            dummy_message,
            'from@example.com',
            [self.user.email],
            fail_silently=False,
        )
