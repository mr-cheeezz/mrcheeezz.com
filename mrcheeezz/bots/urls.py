from django.urls import path

from . import views

urlpatterns = [
  path('', views.bots_list.as_view(), name='botss_list'),
  path('<slug:name>', views.bots_detail.as_view(), name='bots_details'),
  path('<slug:name>/<slug:streamer>', views.bots_detail.as_view(), name='bots_details'),

]