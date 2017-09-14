from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/$', views.UserListView.as_view(), name='user_list'),
    url(r'^team/$', views.TeamCreateView.as_view(), name='team_create'),
    url(r'^invites/$', views.TeamInviteListView.as_view(), name='invite_list'),
]