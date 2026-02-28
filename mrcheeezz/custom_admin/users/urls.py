from django.urls import path
from . import views

urlpatterns = [
  path('', views.user_list, name='user_list'),
  path('<int:user_id>/edit/', views.edit_user, name='user_edit'),
  path('<int:user_id>/delete/', views.delete_user, name='user_delete'),
  path('create-user', views.add_user, name='user_add'),
]