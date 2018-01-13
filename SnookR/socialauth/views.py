from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import redirect
from django.contrib.auth import login

from socialauth.models import FacebookAuth
from accounts.forms import CustomUserModelForm, UserProfileModelForm
from socialauth.forms import FacebookAuthForm


class FacebookAuthView(View):
    def post(self, request, *args, **kwargs):
        if self.forms_are_valid():
            obj, created = FacebookAuth.objects.get_or_create_user(**self.get_forms_data())
            login(request, obj.user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')

        return HttpResponse('Invalid parameters', status=400)

    def forms_are_valid(self):
        return all(f.is_valid() for f in self.get_bound_forms())

    def get_bound_forms(self):
        if not hasattr(self, '_bound_forms'):
            user_form = CustomUserModelForm(self.request.POST)
            profile_form = UserProfileModelForm(self.request.POST)
            facebook_form = FacebookAuthForm(self.request.POST)
            self._bound_forms = [user_form, profile_form, facebook_form]

        return self._bound_forms

    def get_forms_data(self):
        data = dict()
        for form in self.get_bound_forms():
            data.update(form.cleaned_data)

        print(data)
        return data