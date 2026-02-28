from django.urls import path

from . import views

urlpatterns = [
    path('', views.socials_home, name='socials_home'),
    path('<slug:social_id>/edit/', views.edit_social, name='social_edit'),
    path('<slug:social_id>/delete/', views.delete_social, name='social_delete'),
]
