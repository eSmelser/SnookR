# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^division/$', views.DivisionView.as_view(), name='division'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/$', views.SessionView.as_view(), name='session'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/register/$', views.SessionRegisterView.as_view(), name='session_register'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/date/(?P<date>\d{4}-\d{2}-\d{2}_\d{2}-\d{2})/unregister/$', views.SessionUnregisterView.as_view(),
        name='session_unregister'),
]
