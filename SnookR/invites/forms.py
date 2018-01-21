from django import forms
from django.core.exceptions import ValidationError

from accounts.models import User
from substitutes.models import Sub
from teams.models import Team



class TeamForm(forms.Form):
    team = forms.IntegerField(required=True)

    def clean_team(self):
        id_ = self.cleaned_data['team']
        if not Team.objects.filter(pk=id_).exists():
            raise ValidationError('Team with id {} does not exist'.format(id_))

        return id_


class TeamInviteForm(TeamForm):
    invitee = forms.IntegerField(required=True)

    def clean_invitee(self):
        id_ = self.cleaned_data['invitee']
        if not User.objects.filter(pk=id_).exists():
            raise ValidationError('User with id {} does not exist'.format(id_))

        return id_


class SessionEventInviteForm(TeamForm):
    sub = forms.IntegerField(required=True)

    def clean_sub(self):
        print(self.cleaned_data)
        id_ = self.cleaned_data['sub']
        if not Sub.objects.filter(pk=id_).exists():
            raise ValidationError('Sub with id {} does not exist'.format(id_))

        return id_
