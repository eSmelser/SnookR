import calendar

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html

from accounts.models import CustomUser
from core import utils
from divisions.models import SessionEvent, Division, Session, DivRepRequest


class SessionRegistrationForm(forms.Form):
    day = forms.DateTimeField(initial=timezone.now)


def get_instance(id_, model_class):
    if not model_class.objects.filter(id=id_).exists():
        raise ValidationError('{} does not exist'.format(model_class.__name__))

    return model_class.objects.get(id=id_)


class SubForm(forms.Form):
    user = forms.IntegerField(required=True)
    session_event = forms.IntegerField(required=True)

    def clean_user(self):
        id_= self.cleaned_data['user']
        return get_instance(id_, CustomUser)

    def clean_session_event(self):
        id_ = self.cleaned_data['session_event']
        return get_instance(id_, SessionEvent)


class SessionEventIdForm(forms.Form):
    session_event = forms.IntegerField(required=True)

    def clean_session_event(self):
        id_ = self.cleaned_data['session_event_id']
        return get_instance(id_, SessionEvent)


class CreateDivisionForm(forms.ModelForm):
    class Meta:
        model = Division
        fields = ['name']


class CreateSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['name', 'game', 'start', 'end']


class CreateRepeatedEventForm(forms.Form):
    repeated = forms.ChoiceField(choices=[('weekly', 'Weekly'), ('biweekly', 'Bi-Weekly')])
    start_time = forms.TimeField(input_formats=['%I:%M%p', '%-I:%M%p'])
    days = forms.MultipleChoiceField(choices=[(d, d.title()) for d in utils.lower_day_name])
