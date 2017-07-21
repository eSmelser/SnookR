from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<sublist>(\w|[\w-]+))/', views.SublistView.as_view(), name='sublist'),
]
