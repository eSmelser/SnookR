# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils import timezone
from .models import Team, Division

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


class TeamForm(forms.ModelForm):
    division = forms.ModelMultipleChoiceField(queryset=Division.objects.all())

    class Meta:
        model = Team
        fields = ['name', 'players']

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.team_captain = self.user

        obj.save()
        divisions = self.cleaned_data['division']
        for division in divisions:
            obj.division_set.add(division)

        # We call save_m2m because we use commit = False in the super().save() method above
        # which doesn't do the ManyToMany save
        self.save_m2m()
        return obj

