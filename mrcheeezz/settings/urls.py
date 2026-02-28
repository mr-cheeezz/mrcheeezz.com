from django.urls import path
from . import views

urlpatterns = [
    path('', views.Settings.as_view(), name='settings'),
    #path('success', views.Success.as_view(), name="settings:success"),
]