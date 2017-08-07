from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'sublist/(?P<sublist>(\w|[\w-]+))/(?P<session>(\w|[\w-]+))/$', views.SessionView.as_view(), name='session'),
    url(r'sublist/(?P<sublist>(\w|[\w-]+))/(?P<session>(\w|[\w-]+))/register/$', views.RegisterSubSessionView.as_view(), {'next_page': 'home'}, name='session_register'),
    url(r'^sublist/(?P<sublist>(\w|[\w-]+))/$', views.SublistView.as_view(), name='sublist'),
    url(r'^sublists/$', views.SublistsView.as_view(), name='sublists'),
]
