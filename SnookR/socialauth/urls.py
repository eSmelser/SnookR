from django.conf.urls import url

from socialauth import views

urlpatterns = [
    url(r'^socialauth/$', views.FacebookAuthView.as_view(), name='facebook'),
 ]