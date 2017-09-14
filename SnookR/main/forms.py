# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils import timezone
from .models import Team, Division, TeamInvite, CustomUser

phone_regex = validators.RegexValidator(regex=r'^\d{9,15}$',
                                        message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")


class CustomUserMeta:
    model = CustomUser
    fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']


class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(validators=[phone_regex], required=False)
    email = forms.EmailField(required=False)

    class Meta(CustomUserMeta):
        fields = CustomUserMeta.fields + ['password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # No fields are required
        for key in self.fields:
            self.fields[key].required = False

    def clean_password(self):
        return ''


class CustomUserForm(UserCreationForm):
    phone_number = forms.CharField(required=False, validators=[phone_regex])
    email = forms.EmailField(required=True)

    class Meta(CustomUserMeta):
        model = User
        fields = CustomUserMeta.fields + ['password1', 'password2']


class SessionRegistrationForm(forms.Form):
    day = forms.DateTimeField(initial=timezone.now)


class UploadThumbnailForm(forms.Form):
    thumbnail = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['thumbnail'].label = 'Upload thumbnail'


class TeamForm(forms.ModelForm):
    division = forms.ModelMultipleChoiceField(queryset=Division.objects.all())

    class Meta:
        model = Team
        fields = ['division']