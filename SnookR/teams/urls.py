from django.conf.urls import url
from teams import views

urlpatterns = [
    url(r'^$', views.TeamView.as_view(), name='team'),
    url(r'^teams/create/$', views.CreateTeamView.as_view(), name='create_team'),
    url(r'^delete/team/(?P<pk>\d+)/$', views.DeleteTeamView.as_view(), name='delete-team-confirmation'),
]
