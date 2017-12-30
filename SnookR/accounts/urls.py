from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

import accounts.views

urlpatterns = [
    url(r'^login/$', accounts.views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
    url(r'^signup/$', accounts.views.signup, name='signup'),
    url(r'^account/$', accounts.views.AccountView.as_view(), name='account'),
    url(r'^account/change/$', accounts.views.AccountChangeView.as_view(), name='account_change'),
    url(r'^account/delete/$', accounts.views.DeleteAccountView.as_view(), name='account_delete'),
    url(r'^account/delete-redirect/$', accounts.views.DeleteAccountRedirectView.as_view(), name='account_delete_redirect'),
    url(r'^account/delete-success/$', accounts.views.DeleteAccountSuccessView.as_view(), name='account_delete_success'),
    url(r'^password_change/$', accounts.views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^profile/(?P<username>.+)/$', accounts.views.ProfileView.as_view(), name='profile'),
    url(r'^delete_thumbnail/$', accounts.views.DeleteThumbnail.as_view(), name='delete_thumbnail'),
 ]