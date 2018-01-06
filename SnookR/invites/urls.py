from django.conf.urls import url
from invites import views

urlpatterns = [
    url(r'^team-select/$', views.TeamSelectView.as_view(), name='team-select'),
    url(r'^session-select/team/(?P<team_id>\d+)/$', views.SessionSelectView.as_view(), name='session-select'),
    url(r'^session-event-select/team/(?P<team_id>\d+)/session/(?P<session_id>\d+)/$', views.SessionEventSelectView.as_view(), name='session-event-select'),
    url(r'^session-event-invite-confirm/$', views.SessionEventInviteConfirmView.as_view(), name='session-event-invite-confirm'),
    url(r'^session-event-invite-create/$', views.SessionEventInviteCreateView.as_view(), name='session-event-invite-create'),
]
