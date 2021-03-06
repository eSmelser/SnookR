from django.contrib.auth import views as auth_views, authenticate, login
from django.shortcuts import render, get_object_or_404, redirect
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse_lazy, reverse
from django.views.generic import FormView, TemplateView, RedirectView

from accounts.forms import CustomUserLoginForm, CustomUserChangeForm, CustomUserForm, UploadThumbnailForm
from accounts.models import CustomUser, UserProfile
from accounts.emails import send_confirmation_email

class LoginView(auth_views.LoginView):
    authentication_form = CustomUserLoginForm
    template_name = 'accounts/login.html'


class AccountView(FormView):
    template_name = 'accounts/account.html'
    form_class = UploadThumbnailForm
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        profile = UserProfile.objects.get(user=self.request.user)
        profile.thumbnail = self.request.FILES['thumbnail']
        profile.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user'] = CustomUser.from_user(self.request.user)
        return context


class AccountChangeView(FormView):
    template_name = 'accounts/account_change.html'
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('account')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['user'] = CustomUser.from_user(self.request.user)
        return context

    def form_valid(self, form):
        user = CustomUser.from_user(self.request.user)

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
        context['player'] = get_object_or_404(CustomUser, username=kwargs.get('username'))
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


def signup(request):
    if request.method == 'POST':
        form = CustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            email = form.cleaned_data.get('email')
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            phone_number = form.cleaned_data.get('phone_number') or None
            user = authenticate(username=username, password=raw_password, email=email, first_name=first_name,
                                last_name=last_name)
            UserProfile.objects.create(user=user, phone_number=phone_number)
            send_confirmation_email(CustomUser.objects.get(id=user.id))

            if settings.DEBUG:
                login(request, user)

            return redirect('home')
    else:
        form = CustomUserForm()
    return render(request, 'accounts/signup.html', {'form': form})
