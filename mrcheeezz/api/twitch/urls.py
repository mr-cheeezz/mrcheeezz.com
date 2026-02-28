from django.urls import path
from . import views

app_name = 'twitch'

urlpatterns = [
  path('is_live/<str:channel>', views.is_live, name="is_live"),
  path('username_to_id/<str:username>', views.user_to_id, name="user_to_id"),
  path('followage/<str:channel>/<str:username>', views.followage, name='followage'),
]
