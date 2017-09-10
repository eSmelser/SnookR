# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from main.models import UserProfile, Division, Session, CustomUser, Team
from main.forms import (
    CustomUserForm, SessionRegistrationForm,
    TeamForm, CustomUserChangeForm,
    UploadThumbnailForm
)


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
            phone_number = form.cleaned_data.get('phone_number')
            user = authenticate(username=username, password=raw_password, email=email, first_name=first_name,
                                last_name=last_name)
            login(request, user)
            UserProfile.objects.create(user=user, phone_number=phone_number)
            return redirect('home')
    else:
        form = CustomUserForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            try:
                context['user'] = CustomUser.from_user(self.request.user)
            except CustomUser.DoesNotExist:
                pass

        context['teams'] = Team.get_all_related(self.request.user)

        return context


class DivisionListView(TemplateView):
    template_name = 'main/divisions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class DivisionView(TemplateView):
    template_name = 'main/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['division'] = Division.objects.get(slug=kwargs.get('division'))
        return context


class SessionViewMixin(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session_instance(**kwargs)
        context['session'] = session
        context['subs'] = session.get_subs_with_unregister_urls()
        context['user_is_registered'] = session.user_is_registered(self.request.user)
        return context

    def get_session_instance(self, **kwargs):
        session_slug = kwargs.get('session')
        division_slug = kwargs.get('division')
        return Session.objects.get(slug=session_slug, division__slug=division_slug)


class SessionView(SessionViewMixin, TemplateView):
    template_name = 'main/session.html'


class SessionRegisterView(SessionViewMixin, FormView):
    template_name = 'main/session_register.html'
    form_class = SessionRegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        day = form.cleaned_data.get('day')
        session = self.get_session_instance(**self.kwargs)
        session.add_user_as_sub(self.request.user, date=day)
        return super().form_valid(form)


class SessionRegisterSuccessView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('home')


class SessionUnregisterView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        date = datetime.strptime(kwargs.get('date'), Session.date_format)
        session = get_object_or_404(Session, slug=kwargs.get('session'), division__slug=kwargs.get('division'))
        session.remove_user_as_sub(self.request.user, date=date)
        return reverse('home')


class TeamView(TemplateView, LoginRequiredMixin):
    template_name = 'main/team.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['teams'] = Team.get_all_related(self.request.user)
        return context


class CreateTeamView(CreateView, LoginRequiredMixin):
    template_name = 'main/create_team.html'
    form_class = TeamForm
    success_url = reverse_lazy('team')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


class DeleteTeamView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        team = Team.objects.get(slug=kwargs.get('team'), team_captain=self.request.user, id=kwargs.get('pk'))
        team.delete()
        return reverse('team')


class AccountView(FormView):
    template_name = 'main/account.html'
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
    template_name = 'main/account_change.html'
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
    template_name = 'main/profile.html'

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
