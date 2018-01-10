from django.conf.urls import url

from socialauth import views

urlpatterns = [
    url(r'^google-plus/$', views.GoogleLoginView.as_view(), name='login-google'),
    url(r'^signup/$', views.SocialAuthSignup.as_view(), name='socialauth-signup'),
 ]