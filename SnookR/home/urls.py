from django.conf.urls import url
import home.views

urlpatterns = [
    url(r'^$', home.views.HomeView.as_view(), name='home'),
]