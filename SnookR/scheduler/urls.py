from django.conf.urls import url
from scheduler import views

urlpatterns = [
    url(r'^(?P<division>[\w-]+)/', views.TestView.as_view(), name='scheduler'),
    url(r'^$', views.TestView.as_view(), name='scheduler'),
]