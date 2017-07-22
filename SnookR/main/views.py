from django.views.generic.base import TemplateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
	template_name = 'main/home.html'


class LogoutSuccessView(TemplateView):
	template_name = 'registration/logout_success.html'


class ProfileView(TemplateView):
    template_name = 'accounts/profile.html'
