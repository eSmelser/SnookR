from django.conf.urls import url

from scheduler import views

urlpatterns = [
    url(r'^$', views.TestView.as_view(), name='account'),
]