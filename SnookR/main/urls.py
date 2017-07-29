from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from main import views

urlpatterns = [
    url('^logout/$', auth_views.LogoutView.as_view(template_name='user/logout_success.html'), name='logout'),
    url('^login/$', auth_views.LoginView.as_view(template_name='user/login.html'), name='login'),
    url('^password_change/$', auth_views.PasswordChangeView.as_view(template_name='user/password_change_form.html'), name='password_change'),
    url('^password_change_done/$', auth_views.PasswordChangeDoneView.as_view(template_name='user/password_change_done.html'), name='password_change_done'),
    url(r'^accounts/profile/$', views.ProfileView.as_view(), name='profile'),
    url(r'^logout-success/$', views.LogoutSuccessView.as_view(), name='logout-success'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^home/$', views.HomeView.as_view(), name='home'),
]
