from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'division/$', views.DivisionListView.as_view(), name='division_list'),
    url(r'division/(?P<division>(\w|[\w-]+))/$', views.DivisionView.as_view(), name='division'),
    url(r'division/(?P<division>(\w|[\w-]+))/session/(?P<session>(\w|[\w-]+))/$', views.SessionView.as_view(), name='session'),
    url(r'division/(?P<division>(\w|[\w-]+))/session/(?P<session>(\w|[\w-]+))/(?P<location>(\w|[\w-]+))/$',
        views.LocationView.as_view(), name='location'),
    url(r'division/(?P<division>(\w|[\w-]+))/session/(?P<session>(\w|[\w-]+))/(?P<location>(\w|[\w-]+))/register$',
        views.LocationRegisterView.as_view(), name='location_register'),

    url(r'sublist/(?P<sublist>(\w|[\w-]+))/session/(?P<session>(\w|[\w-]+))/register/$', views.RegisterSubSessionView.as_view(), {'next_page': 'home'}, name='session_register'),
    url(r'^sublist/(?P<sublist>(\w|[\w-]+))/$', views.SublistView.as_view(), name='sublist'),
    url(r'^sublists/$', views.SublistsView.as_view(), name='sublists'),
]
