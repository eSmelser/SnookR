from django.conf.urls import include, url
from invites import views

session_event_patterns = ([
    url(r'^session-event/step-1/$', views.SessionEventStartView.as_view(), name='start'),
    url(r'^session-event/step-2/team/(?P<team_id>\d+)/$', views.SessionSelectView.as_view(), name='session-select'),
    url(r'^session-event/step-3/team/(?P<team_id>\d+)/session/(?P<session_id>\d+)/$', views.SessionEventSelectView.as_view(), name='event-select'),
    url(r'^session-event/step-4/confirm/$', views.SessionEventInviteConfirmView.as_view(), name='confirm'),
    url(r'^session-event/step-5/create/$', views.SessionEventInviteCreateView.as_view(), name='create'),
], 'session-event')

urlpatterns = [
    url(r'^invites/$', views.InviteListView.as_view(), name='invites-list'),
    url(r'^direct-sub-invite/(?P<sub_id>\d+)$', views.DirectSubInviteView.as_view(), name='direct-sub-invite'),
    url(r'^session-event/', include(session_event_patterns)),
]
