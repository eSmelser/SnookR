# Copyright &copy; 2017 Evan Smelser
# This software is Licensed under the MIT license. For more info please see SnookR/COPYING

from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
    url(r'^account/$', views.AccountView.as_view(), name='account'),
    url(r'^account_change/$', views.AccountChangeView.as_view(), name='account_change'),
    url(r'^account_delete/$', views.DeleteAccountView.as_view(), name='account_delete'),
    url(r'^account_delete_redirect/$', views.DeleteAccountRedirectView.as_view(), name='account_delete_redirect'),
    url(r'^account_delete_success/$', views.DeleteAccountSuccessView.as_view(), name='account_delete_success'),
    url(r'^password_change/$', views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
    url(r'^profile/(?P<username>.+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^delete_thumbnail/$', views.DeleteThumbnail.as_view(), name='delete_thumbnail'),
    url(r'^team/$', views.TeamView.as_view(), name='team'),
    url(r'^invites/$', views.InviteListView.as_view(), name='invites'),
    url(r'^create_team/$', views.CreateTeamView.as_view(), name='create_team'),
    url(r'^delete_team/(?P<team>[\w-]+)/(?P<pk>[\d]+)$', views.DeleteTeamView.as_view(), name='delete_team'),
    url(r'^division/$', views.DivisionListView.as_view(), name='divisions'),
    url(r'^division/(?P<division>[\w-]+)/$', views.DivisionView.as_view(), name='division'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/$', views.SessionView.as_view(), name='session'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/register/$', views.SessionRegisterView.as_view(), name='session_register'),
    url(r'^division/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/date/(?P<date>\d{4}-\d{2}-\d{2}_\d{2}-\d{2})/unregister/$', views.SessionUnregisterView.as_view(),
        name='session_unregister'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)