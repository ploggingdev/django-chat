from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

app_name = 'chatdemo'

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='home_page'),
    url(r'^register/$', views.RegisterView.as_view(), name='register'),
    url(r'^profile/$', views.ProfileView.as_view(), name='profile'),
    url(
        r'^login/$',
        auth_views.login, { 'redirect_authenticated_user' : True}, name="login",
    ),
    url(
        r'^logout/$',
        views.LogoutView.as_view(), name="logout"
    ),
    url(
        r'^password_change/$',
        auth_views.password_change, {'post_change_redirect' : '/password_change/done'} ,name="password_change"
    ),
    url(
        r'^password_change/done/$',
        auth_views.password_change_done ,name="password_change_done"
    ),
    url(
        r'^password_reset/$',
        auth_views.password_reset, {'post_reset_redirect' : '/password_reset/done', 'from_email' : 'djangochat@ploggingdev.com'} ,name="password_reset"
    ),
    url(
        r'^password_reset/done/$',
        auth_views.password_reset_done, name="password_reset_done"
    ),
    url(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm, {'post_reset_redirect' : '/reset/done'}, name="password_reset_confirm"
    ),
    url(
        r'^reset/done/$',
        auth_views.password_reset_complete, name="password_reset_complete"
    ),
]