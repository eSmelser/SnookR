from django.conf.urls import url
from api import views
from messaging import views as messaging_views

urlpatterns = [
    url(r'^auth/user/$', views.UserView.as_view(), name='user'),
    url(r'^users/$', views.UserListView.as_view(), name='user-list'),
    url(r'^messages/$', views.MessageListView.as_view(), name='message-list'),
    url(r'^team/$', views.TeamView.as_view(), name='team'),
    url(r'^invites/$', views.TeamInviteListView.as_view(), name='invite-list'),
    url(r'^invites/(?P<pk>[0-9]+)/$', views.TeamInviteUpdateView.as_view(), name='invite'),
    url(r'^unregistered-players/$', views.NonUserPlayerListCreateView.as_view(), name='unregistered-players'),
    url(r'^sessions/$', views.SessionListView.as_view(), name='sessions'),
    url(r'^session-events/$', views.SessionEventListView.as_view(), name='session-events'),
    url(r'^subs/$', views.SubListView.as_view(), name='sub-list'),
    url(r'^search-user/$', views.SearchUserView.as_view(), name='search-user'),
    url(r'^session-event-invites/$', views.SessionEventInviteListView.as_view(), name='session-event-invite-list'),
    url(r'^session-event-invites/(?P<pk>[0-9]+)/$', views.SessionEventInviteView.as_view(), name='session-event-invite'),
    url(r'^messaging/message/new/$', messaging_views.MessageNewView.as_view(), name='new-message'),
    url(r'^messaging/message/$', messaging_views.MessageCreateView.as_view(), name='message-detail-create'),
    url(r'^tokeninput/$', views.TokenInputListView.as_view(), name='tokeninput'),
]
