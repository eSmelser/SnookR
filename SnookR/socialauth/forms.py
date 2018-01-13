from django import forms
from socialauth.models import FacebookAuth


class FacebookAuthForm(forms.ModelForm):
    class Meta:
        model = FacebookAuth
        fields = ['facebook_id']

