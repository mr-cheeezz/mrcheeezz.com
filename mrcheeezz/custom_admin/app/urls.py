from django.urls import path
from . import views

urlpatterns = [
    path('<str:app_name>/', views.app_models, name='app_home'),
    path('<str:app_name>/<str:model_name>/', views.model_instances, name='model_instances'),
    path('<str:app_name>/<str:model_name>/add/', views.add_instance, name='add_instance'),
    path('<str:app_name>/<str:model_name>/<str:pk>/edit/', views.edit_instance, name='edit_instance'),
    path('<str:app_name>/<str:model_name>/<str:pk>/delete/', views.delete_instance, name='delete_instance'),
]