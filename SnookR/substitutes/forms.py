# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from accounts.models import CustomUser
from substitutes.models import Sub, SessionEvent


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