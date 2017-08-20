# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils import timezone

phone_regex = validators.RegexValidator(regex=r'^\d{9,15}$',
                                        message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")


class CustomUserForm(UserCreationForm):
    phone_number = forms.CharField(validators=[phone_regex])
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'phone_number']


class SessionRegistrationForm(forms.Form):
    day = forms.DateTimeField(initial=timezone.now)
