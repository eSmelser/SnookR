from django.conf.urls import url
from api import views

urlpatterns = [
    url(r'^users/$', views.UserListView.as_view(), name='user_list'),
]