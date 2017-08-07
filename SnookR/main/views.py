from django.views.generic.base import TemplateView
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from main.models import Player
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
            user = authenticate(username=username, password=raw_password, email=email, first_name=first_name, last_name=last_name)
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
