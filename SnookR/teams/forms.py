from django import forms

from accounts.models import CustomUser
from divisions.models import Division
from teams.models import Team


class TeamForm(forms.ModelForm):
    division = forms.ModelMultipleChoiceField(queryset=Division.objects.all())

    class Meta:
        model = Team
        fields = ['division']


class CaptainForm(forms.Form):
    division = forms.ModelChoiceField(required=True, queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['division'].queryset = self.initial['user'].divisions_set.all()

    def clean(self):
        super().clean()
        users = CustomUser.objects.filter(pk__in=self.data.getlist('user'))
        if not users.exists():
            raise forms.ValidationError('Must select at least one user to be a captain')

        self.cleaned_data['users'] = CustomUser.objects.filter(pk__in=self.data.getlist('user'))
