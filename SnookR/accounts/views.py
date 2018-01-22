from django.contrib.auth import views as auth_views, authenticate, login, get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView, RedirectView

from accounts.forms import CustomUserLoginForm, CustomUserChangeForm, CustomUserCreationForm, UploadThumbnailForm, \
    ChooseDivisionForm
from accounts.models import User, UserProfile
from accounts.emails import send_confirmation_email
from teams.models import CaptainRequest


class LoginView(auth_views.LoginView):
    authentication_form = CustomUserLoginForm
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['SOCIAL_AUTH_GOOGLE_PLUS_KEY'] = settings.SOCIAL_AUTH_GOOGLE_PLUS_KEY
        context['SOCIAL_AUTH_FACEBOOK_KEY'] = settings.SOCIAL_AUTH_FACEBOOK_KEY
        context['SOCIAL_AUTH_FACEBOOK_API_VERSION'] = settings.SOCIAL_AUTH_FACEBOOK_API_VERSION
        return context


class AccountView(FormView):
    template_name = 'accounts/account.html'
    form_class = UploadThumbnailForm
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        profile = UserProfile.objects.get(user=self.request.user)
        profile.thumbnail = self.request.FILES['thumbnail']
        profile.save()
        return super().form_valid(form)


class AccountChangeView(FormView):
    template_name = 'accounts/account_change.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        user = self.request.user

        # Update user only with fields with non-empty values
        for field in self.form_class.Meta.fields:
            value = form.cleaned_data.get(field, False)
            if value:
                setattr(user, field, value)

        user.save()
        return super().form_valid(form)


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['player'] = get_object_or_404(User, username=kwargs.get('username'))
        return context


class DeleteThumbnail(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        profile = get_object_or_404(UserProfile, user=self.request.user)
        profile.thumbnail = None
        profile.save()
        return reverse('account')


class DeleteAccountView(TemplateView):
    template_name = 'accounts/account_delete.html'


class DeleteAccountRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.request.user.delete()
        return reverse('account_delete_success')


class DeleteAccountSuccessView(TemplateView):
    template_name = 'accounts/account_delete_success.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('account')


class SignUpView(TemplateView):
    template_name = 'accounts/signup.html'


class PlayerSignUpView(FormView):
    template_name = 'accounts/signup_player.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.save()
        username = form.cleaned_data.get('username')
        raw_password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)
        profile = UserProfile.objects.create(user=user)
        profile.send_confirmation_email()
        return super().form_valid(form)


class CaptainSignUpView(PlayerSignUpView):
    template_name = 'accounts/signup_captain.html'
    success_url = reverse_lazy('signup-captain-choose-division')


class CaptainChooseDivisionView(LoginRequiredMixin, FormView):
    template_name = 'accounts/signup_captain_choose_division.html'
    form_class = ChooseDivisionForm
    success_url = reverse_lazy('signup-captain-success')

    def form_valid(self, form):
        # Retrieve chosen division
        division = form.cleaned_data['division']

        # Create a team captain status request
        request = CaptainRequest.objects.create(division=division, user=self.request.user)

        # Send a team captain status request notification to division representative
        request.send_notification()
        return super().form_valid(form)


class CaptainSignUpSuccessView(TemplateView):
    template_name = 'accounts/signup_captain_success.html'
