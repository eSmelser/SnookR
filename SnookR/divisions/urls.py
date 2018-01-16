from django.conf.urls import url

from divisions import views

urlpatterns = [
    url(r'^divisions/$', views.DivisionListView.as_view(), name='divisions'),
    url(r'^divisions/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/session-events/(?P<session_event>[0-9]+)/$',
        views.SessionEventDetailView.as_view(), name='session-event-detail'),
    url(r'^divisions/(?P<division>[\w-]+)/$', views.DivisionView.as_view(), name='division'),
    url(r'^divisions/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/$', views.SessionView.as_view(), name='session'),
    url(
        r'^divisions/(?P<division>[\w-]+)/session/(?P<session>[\w-]+)/date/(?P<date>\d{4}-\d{2}-\d{2}_\d{2}-\d{2})/unregister/$',
        views.SessionUnregisterView.as_view(),
        name='session-unregister'),
    url(r'^search/(?P<search_type>substitute|session)/$', views.SearchView.as_view(), name='search'),
    url(r'^session-events/(?P<pk>[0-9]+)/register/$', views.SessionEventRegisterView.as_view(),
        name='session-event-register'),
    url(r'^session-events/(?P<pk>[0-9]+)/unregister/$', views.SessionEventUnregisterView.as_view(),
        name='session-event-unregister'),
    url(r'^session-events/(?P<pk>[0-9]+)/$', views.SessionEventView.as_view(), name='session-event'),
]
