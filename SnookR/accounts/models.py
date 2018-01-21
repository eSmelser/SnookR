import random
from datetime import timedelta

from django.contrib.auth.models import UserManager, User
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
        permissions = (
            ('can_permit_add_team', 'Can permit other users to have add_team permissions (i.e., is Division Rep)'),
        )

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

    @property
    def get_absolute_url(self):
        return reverse('profile', kwargs={'username': self.username})

    @property
    def invites_count(self):
        return SessionEventInvite.objects.filter(sub__user=self).pending().count() + self.teaminvite_set.pending().count()

    @staticmethod
    def unique_username(first_name, last_name):
        username = first_name + last_name
        while CustomUser.objects.filter(username=username).exists():
            username = first_name + last_name + ''.join(random.randint(0, 9) for _ in range(4))

        return username

    def is_division_rep(self):
        return self.divisions_set.all().exists()

    def is_captain(self):
        return self.is_authenticated() and self.captain_divisions.exists()

    @cached_property
    def captain_divisions(self):
        query = Q(name__startswith='division') & Q(name__endswith='team_captain')
        groups = self.groups.filter(query)
        ids = []
        for group in groups:
            name = group.name
            id_ = name.lstrip('division.').rstrip('.team_captain') # 'division.2.team_captain' -> '2'
            id_ = int(id_)
            ids.append(id_)

        return Division.objects.filter(pk__in=ids)


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
