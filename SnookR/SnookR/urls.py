"""SnookR URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from sublist import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^(?P<sublist>(\w|[\w-]+))/', views.SublistView.as_view(), name='sublist'),
	url(r'^wichita/', views.wichita),
	url(r'^riverroadhouse/', views.river_roadhouse),
	url(r'^mcanultyandbarrys/', views.mcanulty_and_barrys),
	url(r'^local66/', views.local66),
	url(r'^watertrough/', views.watertrough),
	url(r'^fortunestar/', views.fortune_star),
	url(r'^pub181/', views.pub181),
	url(r'^outereastside/', views.outer_eastside),
]
