from django.urls import path

from . import views

app_name = "steam"

urlpatterns = [
    path("player/<str:steam_id>", views.player_summary, name="player_summary"),
    path("current-game/<str:steam_id>", views.current_game, name="current_game"),
]
