from django import forms
from django.core.exceptions import ValidationError

from accounts.models import CustomUser
from teams.models import Team


class TeamInviteForm(forms.Form):
    invitee = forms.IntegerField(required=True)
    team = forms.IntegerField(required=True)

    def clean_invitee(self):
        id_ = self.cleaned_data['invitee']
        if not CustomUser.objects.filter(pk=id_).exists():
            raise ValidationError('User with id {} does not exist'.format(id_))

        return id_

    def clean_team(self):
        id_ = self.cleaned_data['team']
        if not Team.objects.filter(pk=id_).exists():
            raise ValidationError('Team with id {} does not exist'.format(id_))

        return id_