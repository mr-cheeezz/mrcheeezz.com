from django.urls import path

from . import views

urlpatterns = [
  path('', views.about.as_view(), name="about"),
]