from django.conf.urls import url

from divisions import views

urlpatterns = [
    url(r'^divisions/$', views.DivisionListView.as_view(), name='divisions'),
    url(r'^divisions/(?P<division>[\w-]+)/session/(?P<session>\d+)/session-events/(?P<session_event>\d+)/$',
        views.SessionEventDetailView.as_view(), name='session-event-detail'),
    url(r'^divisions/(?P<division>[\w-]+)/$', views.DivisionView.as_view(), name='division'),
    url(r'^divisions/(?P<division>\d+)/session/(?P<session>\d+)/$', views.SessionView.as_view(), name='session'),
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
    url(r'^create-division/', views.CreateDivisionView.as_view(), name='create-division'),
    url(r'^div-rep-divisions/$', views.DivRepDivisionsList.as_view(), name='div-rep-divisions-list'),
    url(r'^div-rep-division/(?P<pk>[0-9]+)/create-session/$', views.DivRepCreateSessionView.as_view(), name='div-rep-create-session'),
    url(r'^div-rep-division/session/(?P<pk>[0-9]+)/create-session-event/$', views.DivRepCreateSessionEventView.as_view(),
        name='div-rep-create-session-event'),
]
