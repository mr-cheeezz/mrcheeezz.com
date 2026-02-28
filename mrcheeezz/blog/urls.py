from django.urls import path
from . import views

app_name = 'blog'
urlpatterns = [
  path('', views.BlogList.as_view(), name='blog'),
  path('<slug:slug>/', views.PostDetail.as_view(), name='post_detail'),
  path('delete/<int:post_id>/', views.DeletePost.as_view(), name='delete_post'),
  path('edit/<int:pk>/', views.EditPost.as_view(), name='edit_post'),
  path('create', views.CreatePost.as_view(), name='create_post'),
]