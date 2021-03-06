from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^auth/user/$', views.UserView.as_view(), name='user'),
    url(r'^users/$', views.UserListView.as_view(), name='user_list'),
    url(r'^team/$', views.TeamView.as_view(), name='team'),
    url(r'^invites/$', views.TeamInviteListView.as_view(), name='invite_list'),
    url(r'^invites/(?P<pk>[0-9]+)/$', views.TeamInviteUpdateView.as_view(), name='invite'),
    url(r'^unregistered-players/$', views.NonUserPlayerListCreateView.as_view(), name='unregistered_players'),
    url(r'^sessions/$', views.SessionListView.as_view(), name='sessions'),
    url(r'^session-events/$', views.SessionEventListView.as_view(), name='session_events'),
    url(r'^subs/$', views.SubListView.as_view(), name='sub_list'),
    url(r'^search-user/$', views.SearchUserView.as_view(), name='search_user'),
    url(r'^session-event-invites/$', views.SessionEventInviteListView.as_view(), name='session_event_invite_list'),
    url(r'^session-event-invites/(?P<pk>[0-9]+)/$', views.SessionEventInviteView.as_view(), name='session_event_invite'),
]
