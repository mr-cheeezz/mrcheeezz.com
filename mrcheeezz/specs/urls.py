from django.urls import path

from . import views

urlpatterns = [
  path('', views.specs_list.as_view(), name='specs_list'),
  path('<slug:slug>', views.specs_detail.as_view(), name='specs_details')
]