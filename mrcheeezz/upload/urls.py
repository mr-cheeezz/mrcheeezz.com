from django.urls import path

from . import views

urlpatterns = [
  path('', views.UploadImage.as_view(), name='upload'),
  path('success/<int:img_id>/', views.UploadSuccess.as_view(), name='upload_success'),
  path('delete/<int:pk>/', views.DeleteUpload.as_view(), name='delete_image'),
]