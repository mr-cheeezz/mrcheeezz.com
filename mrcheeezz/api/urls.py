from django.urls import path, include
from . import views

urlpatterns = [
  path('roblox/', include('api.roblox.urls')),
  path('twitch/', include('api.twitch.urls')),
  path('spotify/', include('api.spotify.urls')),
  path('steam/', include('api.steam.urls')),
  path('7tv/', include('api.seven_tv.urls')),
  path('bttv/', include('api.bttv.urls')),
  path('ffz/', include('api.ffz.urls')),

  path('schema/', views.openapi_schema_view, name='api-openapi-schema'),
  path('', views.SwaggerDocsView.as_view(), name="api-docs"),
  path('<path:extra>/', views.api_404),
]
