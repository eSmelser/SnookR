# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from datetime import datetime
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from main.models import Player, Division, Sub, Session
from main.forms import CustomUserForm, SessionRegistrationForm


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
            player = Player.objects.create(user=user, phone_number=phone_number)

            print('user=', user)
            print('player=', player)
            return redirect('home')
    else:
        form = CustomUserForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated():
            player = Player.objects.get(user=self.request.user)
            context['player'] = player
            context['subs'] = Sub.objects.filter(player=player)
        return context


class DivisionView(TemplateView):
    template_name = 'main/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
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
