from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.MessagingView.as_view(), name='messaging'),
    #url(r'^$', views.MessagingRootView.as_view(), name='root'),
]