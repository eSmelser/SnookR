# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django import forms
from django.utils import timezone

class SessionRegistrationForm(forms.Form):
    day = forms.DateTimeField(initial=timezone.now)
