from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^auth/user/$', views.UserView.as_view(), name='user'),
    url(r'^users/$', views.UserListView.as_view(), name='user_list'),
    url(r'^team/$', views.TeamView.as_view(), name='team'),
    url(r'^invites/$', views.TeamInviteListView.as_view(), name='invite_list'),
]