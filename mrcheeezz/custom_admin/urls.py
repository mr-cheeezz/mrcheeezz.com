from django.urls import include, path

from . import views

app_name = 'custom_admin'

urlpatterns = [
  path('', views.Home.as_view(), name='home'),
  path('settings', views.site_settings, name='settings'),
  path('socials/', include('custom_admin.socials.urls')),
  path('restart', views.restart_website, name='website_restart'),
  path('logs', views.logs, name='logs'),
  path('users/', include('custom_admin.users.urls')),
  path('apps/', include('custom_admin.app.urls')),
]
