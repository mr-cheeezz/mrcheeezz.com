from django.urls import path
from . import views

app_name = 'spotify'

urlpatterns = [
  path('now-playing-card', views.now_playing_owner_card, name='now_playing_card_owner_alias'),
  path('owner/now-playing-card', views.now_playing_owner_card, name='owner_now_playing_card'),
  path('now-playing-card/<str:user_id>', views.now_playing_card, name='now_playing_card'),
  path('now-playing/<str:user_id>', views.now_playing, name='now_playing'),
  path('top-tracks/<str:user_id>', views.top_tracks, name='top_tracks'),
  path('last-song/<str:user_id>', views.last_song, name='last_song'),
  path('player-queue/<str:user_id>', views.player_queue, name='player_queue'),
  path('song-info/<str:user_id>', views.song_info, name='player_queue'),
  path('queue-song/<str:user_id>', views.queue_song, name='add_queue'),
  path('skip-song/<str:user_id>', views.skip_current_song, name='skip_song'),
]
