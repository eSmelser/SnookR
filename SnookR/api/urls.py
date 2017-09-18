from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^auth/user/$', views.UserView.as_view(), name='user'),
    url(r'^users/$', views.UserListView.as_view(), name='user_list'),
    url(r'^team/$', views.TeamView.as_view(), name='team'),
    url(r'^invites/$', views.TeamInviteListView.as_view(), name='invite_list'),
    url(r'^invites/(?P<pk>[0-9]+)/$', views.TeamInviteUpdateView.as_view(), name='invite'),
    url(r'^unregistered_players/$', views.NonUserPlayerListCreateView.as_view(), name='unregistered_players'),
]
