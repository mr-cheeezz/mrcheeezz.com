from django.urls import path
from . import views

urlpatterns = [
  path('presence/<str:username>', views.presence, name='presence'),
  path('max_players/<str:type>/<str:id>', views.max_players, name='max_players'),
  path('user/<str:type>/<str:username>', views.user_info, name="user_info"),

  path('convert-username-to-id/<str:username>/', views.convert_username_to_id, name='convert_username_to_id'),
]
