from django.urls import path

from . import views

app_name = "ffz"

urlpatterns = [
    path("emote/<str:code>", views.emote, name="emote"),
]
