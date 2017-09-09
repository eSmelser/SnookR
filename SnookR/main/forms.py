# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils import timezone
from .models import Team, Division, NonUserPlayer, CustomUser

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
    phone_number = forms.CharField(validators=[phone_regex])
    email = forms.EmailField(required=True)

    class Meta(CustomUserMeta):
        model = User
        fields = CustomUserMeta.fields + ['password1', 'password2']


class SessionRegistrationForm(forms.Form):
    day = forms.DateTimeField(initial=timezone.now)


class TeamForm(forms.ModelForm):
    division = forms.ModelMultipleChoiceField(queryset=Division.objects.all())
    extra_player_1 = forms.CharField(max_length=200, required=False)
    extra_player_2 = forms.CharField(max_length=200, required=False)
    extra_player_3 = forms.CharField(max_length=200, required=False)
    extra_player_4 = forms.CharField(max_length=200, required=False)
    extra_player_5 = forms.CharField(max_length=200, required=False)
    extra_player_6 = forms.CharField(max_length=200, required=False)
    extra_player_7 = forms.CharField(max_length=200, required=False)
    extra_player_8 = forms.CharField(max_length=200, required=False)

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

        extra_player_count = 8
        for i in range(extra_player_count):
            field_name = 'extra_player_{}'.format(i + 1)
            name = self.cleaned_data[field_name]
            if name:
                NonUserPlayer.objects.create(name=name, team=obj)

        # We call save_m2m because we use commit = False in the super().save() method above
        # which doesn't do the ManyToMany save
        self.save_m2m()
        return obj
