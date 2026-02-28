from django.urls import path
from django.conf import settings

from . import views

urlpatterns = [
  path('', views.ProjectList.as_view(), name='project_list'),
  path('<slug:slug>/', views.ProjectDetail.as_view(), name='project_details')
]
