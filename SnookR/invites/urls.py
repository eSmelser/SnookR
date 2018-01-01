from django.conf.urls import url
from invites import views

urlpatterns = [
    url(r'^session-events/(?P<session_event>\d+)/subs/(?P<sub>\d+)/$', views.SessionEventInviteView.as_view(), name='session_event_invite'),
]