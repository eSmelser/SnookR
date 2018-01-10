from django import forms
from django.core import validators
from accounts.models import CustomUser

phone_regex = validators.RegexValidator(regex=r'^\d{9,15}$',
                                        message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")

class SocialAuthSignupForm(forms.ModelForm):
    phone_number = forms.CharField(required=False)

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']