from django.views.generic.base import TemplateView
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
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


class DivisionView(TemplateView):
    template_name = 'main/division.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['divisions'] = Division.objects.all()
        return context


class SessionTemplateMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.get_session_instance(**kwargs)
        context['session'] = session
        context['session_url'] = session.get_register_url()
        context['subs'] = session.subs.all()
        return context

    def get_session_instance(self, **kwargs):
        return Session.objects.get(slug=kwargs.get('session'), division__slug=kwargs.get('division'))


class SessionView(SessionTemplateMixin, TemplateView):
    template_name = 'main/session.html'

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class SessionRegisterView(TemplateView, SessionTemplateMixin):
    template_name = 'main/session_register.html'

    def get(self, request, *args, **kwargs):
        session = self.get_session_instance(**kwargs)
        session.add_user_as_sub(self.request.user)
        return super().get(request, *args, **kwargs)
