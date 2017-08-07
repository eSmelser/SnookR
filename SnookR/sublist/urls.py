from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'register_sub$', views.RegisterSubView.as_view(), {'next_page': 'home'}, name='register_sub'),
    url(r'^sublist/(?P<sublist>(\w|[\w-]+))/$', views.SublistView.as_view(), name='sublist'),
    url(r'^sublists/$', views.SublistsView.as_view(), name='sublists'),
]
