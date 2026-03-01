from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from api import views as api_views
from update import views as update_views
from about import views as about_views
from .version import version
from .log import logger
from . import views

urlpatterns = [
    path('', include('home.urls')),
    path('contact', include('contact.urls')),
    path('blog/', include('blog.urls')),
    path('about', include('about.urls')),
    path('about/', include('about.urls')),

    path('about/settings', about_views.about_settings, name="about_settings"),
    path('about/settings/', about_views.about_settings, name="about_settings_slash"),

    path('changelog', update_views.update_log, name='changelog'),
    path('copyright', update_views.copyright, name='legal'),

    path('bots/', include('bots.urls')),
    path('projects/', include('projects.urls')),
    path('specs/', include('specs.urls')),

    path('upload/', include('upload.urls')),
    path('tags', include('tags.urls')),

    path('accounts/logout', views.logout.as_view(), name="logout"),
    path('accounts/login', views.login.as_view(), name="login"),
    
    path('admin/', include('custom_admin.urls')),
    path('a/', admin.site.urls),

    path('redirect', views.redirect, name='redir'),

    path('api/', include('api.urls')),

    path('api/game', views.fetch_game),
    path('api/steam/game', views.fetch_steam_data),
    path('api/roblox/game', views.fetch_roblox_data),
    path('api/spotify/is-playing', views.check_spotify_playing),
    path('api/steam/change-time', views.update_game_time),
    path('api/steam/reset-time', views.reset_game_time),
    path('api/steam/get-time', views.get_game_time),

    path('conversion/roblox/username-to-id', api_views.username_to_id),
    
    path('spotify/connect/', api_views.spotify_connect, name='spotify_connect'),
    path('spotify/callback/', api_views.spotify_callback, name='spotify_callback'),
    path('spotify/api/connect/', api_views.spotify_api_connect, name='spotify_api_connect'),
    path('spotify/api/callback/', api_views.spotify_api_callback, name='spotify_api_callback'),
    path('spotify/success/', api_views.spotify_success, name='spotify_success'),
    path('discord/connect/', api_views.discord_connect, name='discord_connect'),
    path('discord/callback/', api_views.discord_callback, name='discord_callback'),
    path('roblox/connect/', api_views.roblox_connect, name='roblox_connect'),
    path('roblox/callback/', api_views.roblox_callback, name='roblox_callback'),
    path('spotify_auth', api_views.spotify_auth, name='spotify_auth'),
    path('twitch_auth', api_views.twitch_auth, name='twitch_auth'),
    path('roblox_auth', api_views.roblox_auth, name='roblox_auth'),
    path('discord_auth', api_views.discord_auth, name='discord_auth'),
]

# Serve uploaded media in all environments as a fallback.
# In production, nginx can/should still handle /media directly.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    handler400 = views.error_400
    handler401 = views.error_401
    handler403 = views.error_403
    handler404 = views.error_404
    handler500 = views.error_500
    handler502 = views.error_502

logger.info(f'Started website v{version}')
