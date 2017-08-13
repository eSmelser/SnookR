from django.views.generic.base import TemplateView, RedirectView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.urls import reverse
from main.models import Player, Division, Sub, Session
from main.forms import CustomUserForm


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
            context['player'] = Player.objects.get(user=self.request.user)
        return context


class DivisionView(TemplateView):
    template_name = 'main/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class SessionViewMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session_instance(**kwargs)
        context['session'] = session
        context['subs'] = session.subs.all()
        context['user_is_registered'] = session.user_is_registered(self.request.user)
        return context

    def get_session_instance(self, **kwargs):
        return Session.objects.get(slug=kwargs.get('session'), division__slug=kwargs.get('division'))


class SessionView(SessionViewMixin, TemplateView):
    template_name = 'main/session.html'


class SessionRegisterView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        session = self.get_session_instance(**kwargs)
        session.add_user_as_sub(self.request.user)
        return reverse('home')


class SessionUnregisterView(RedirectView, SessionViewMixin):
    def get_redirect_url(self, *args, **kwargs):
        session = self.get_session_instance(**kwargs)
        session.remove_user_as_sub(self.request.user)
        return reverse('home')
