from django.urls import path

from . import views

app_name = "seven_tv"

urlpatterns = [
    path("emote/<str:name>", views.emote, name="emote"),
    path("emote-id/<str:emote_id>", views.emote_by_id, name="emote_by_id"),
]
