from crispy_forms.bootstrap import StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout
from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm, UserCreationForm
from django.contrib.auth.models import User
from django.core import validators
from django.utils.translation import gettext_lazy as _

from accounts.models import User, UserProfile
from divisions.models import Division

phone_regex = validators.RegexValidator(regex=r'^\d{9,15}$',
                                        message="Phone number must be entered in the format: '999999999'. Up to 15 digits allowed.")


class CustomUserModelForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class UserProfileModelForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'thumbnail', 'image_url']


class CustomPasswordInput(forms.PasswordInput):
    """This sets the PassWordInput CSS class to form-control for Bootstrap 3"""

    def get_context(self, name, value, attrs):
        attrs['class'] = 'form-control'
        return super().get_context(name, value, attrs)


text = forms.TextInput(attrs={'class': 'form-control'})


class CustomUserMeta:
    model = User
    fields = ['username', 'first_name', 'last_name', 'email', 'phone_number']

    widgets = {
        'username': text,
        'first_name': text,
        'last_name': text,
        'phone_number': text,
    }


class CustomUserLoginForm(AuthenticationForm):
    pass


class CustomUserChangeForm(UserChangeForm):
    phone_number = forms.CharField(validators=[phone_regex], required=False)
    email = forms.EmailField(required=False)

    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=CustomPasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    class Meta(CustomUserMeta):
        fields = CustomUserMeta.fields + ['password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # No fields are required
        for key in self.fields:
            self.fields[key].required = False

    def clean_password(self):
        return ''


class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(required=False, validators=[phone_regex], widget=text, label=_("Phone Number"))
    email = forms.EmailField(required=True, widget=text)

    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=CustomPasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label=_("Confirm Password"),
        strip=False,
        widget=CustomPasswordInput,
        help_text=password_validation.password_validators_help_text_html(),
    )

    class Meta(CustomUserMeta):
        model = User
        fields = CustomUserMeta.fields + ['password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'email',
            'username',
            'first_name',
            'last_name',
            'phone_number',
            'password1',
            'password2',
            StrictButton('Sign up', css_class='btn-default', type='submit'),
        )


class UploadThumbnailForm(forms.Form):
    thumbnail = forms.ImageField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['thumbnail'].label = 'Upload thumbnail'


class ChooseDivisionForm(forms.Form):
    division = forms.ModelChoiceField(queryset=Division.objects.all())