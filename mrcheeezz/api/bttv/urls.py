from django.urls import path

from . import views

app_name = "bttv"

urlpatterns = [
    path("emote/<str:code>", views.emote, name="emote"),
]
