from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('create-folder/', views.CreateFolderView.as_view(), name='create_folder'),
    path('folders/<int:pk>/', views.FolderDetailView.as_view(), name='folder_detail'),
]