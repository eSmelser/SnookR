from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    url('^', include('django.contrib.auth.urls')),
    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^logout-success/$', views.LogoutSuccessView.as_view(), name='logout-success'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
]
