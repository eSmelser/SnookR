from django import forms
from substitutes.models import Division
from teams.models import Team

class TeamForm(forms.ModelForm):
    division = forms.ModelMultipleChoiceField(queryset=Division.objects.all())

    class Meta:
        model = Team
        fields = ['division']
