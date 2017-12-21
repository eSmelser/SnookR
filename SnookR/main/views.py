# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

import itertools
from datetime import datetime
from functools import reduce
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView, CreateView
from django.contrib.auth import login, authenticate

import django.contrib.auth.views as auth_views
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.db.models import Q
from main.models import UserProfile, Division, Session, SessionEvent, CustomUser, Team, Sub
from main.forms import (
    CustomUserForm, SessionRegistrationForm,
    CustomUserLoginForm,
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
    return render(request, 'user/signup.html', {'form': form})


class LoginView(auth_views.LoginView):
    authentication_form = CustomUserLoginForm
    template_name = 'user/login.html'


class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            try:
                context['user'] = CustomUser.from_user(self.request.user)
                sessions = set(sub.session_event.session for sub in
                               Sub.objects.select_related('session_event').filter(user=self.request.user))
                divisions = Division.objects.filter(session__in=sessions)
                context['divisions'] = set(divisions)
                context['sessions'] = sorted(list(sessions), key=lambda obj: obj.name)

            except CustomUser.DoesNotExist:
                pass
        else:
            context['sub_count'] = len(set(sub.user for sub in Sub.objects.all()))
            context['sessions'] = Session.objects.all()
            context['sessions_count'] = len(Session.objects.all())

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
        now = datetime.now()
        session_event = SessionEvent.objects.filter(session=session, date__month=now.month).order_by('date').first()
        subs = Sub.objects.filter(session_event=session_event)

        context['session'] = session
        context['session_event'] = session_event
        if self.request.user.is_authenticated():
            context['user_is_registered'] = subs.filter(user=self.request.user).exists()
            context['subs'] = subs.exclude(user=self.request.user)
            try:
                context['current_user_sub'] = subs.get(user=self.request.user)
            except Sub.DoesNotExist:
                pass
        else:
            context['user_is_registered'] = False
            context['subs'] = subs
            context['current_user_sub'] = None

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


class CreateTeamView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    template_name = 'main/create_team.html'
    form_class = TeamForm
    success_url = reverse_lazy('home')
    permission_required = 'main.add_team'
    login_url = '/login/'


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


class InviteListView(TemplateView):
    template_name = 'main/invites.html'


class DeleteAccountView(TemplateView):
    template_name = 'main/account_delete.html'


class DeleteAccountRedirectView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        self.request.user.delete()
        return reverse('account_delete_success')


class DeleteAccountSuccessView(TemplateView):
    template_name = 'main/account_delete_success.html'


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = 'main/password_change.html'
    success_url = reverse_lazy('account')


class SearchView(TemplateView):
    template_name = 'main/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        terms = self.request.GET['query'].split()
        search_type = kwargs.get('search_type', None)

        if search_type == 'session':
            # Build a Q object that check if the name column contains any of the terms in search
            q_object = reduce(lambda q1, q2: q1 | q2, (Q(name__contains=term) for term in terms), Q())

            # Filter sessions on the previously built Q object
            context['results'] = Session.objects.filter(q_object)
        elif search_type == 'substitute':
            # Build a Q object that filters for available substitutes that have last or first names that
            # starts with any of the search terms

            # 1.) Define all the Q objects
            first_name_queries = (Q(user__first_name__istartswith=term) for term in terms)
            last_name_queries = (Q(user__last_name__istartswith=term) for term in terms)

            # 2.) Reduce the Q objects into a single Q object by using the OR operator on each one together
            q_object = reduce(lambda q1, q2: q1 | q2, itertools.chain(last_name_queries, first_name_queries), Q())

            # 3.) Get the distinct IDs of each user to remove duplicates
            distinct_ids = Sub.objects.filter(q_object).values('user').distinct()

            # 4.) Filter on the distinct ids and set results
            context['results'] = CustomUser.objects.filter(id__in=distinct_ids)
        else:
            raise Http404('Invalid URL kwargs: ' + str(kwargs))

        return context


class SessionEventRegisterView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        Sub.objects.create(session_event=SessionEvent.objects.get(id=id), user=self.request.user)
        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('home')


class SessionEventUnregisterView(LoginRequiredMixin, RedirectView):
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        qs = Sub.objects.filter(session_event=SessionEvent.objects.get(id=id), user=self.request.user)
        if qs.exists():
            qs.delete()

        return super().get(request, *args, **kwargs)

    def get_redirect_url(self, *args, **kwargs):
        return reverse('home')
