from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('foldera/create/', views.CreateFolderView.as_view(), name='create_folder'),
    path('folders/<int:pk>/', views.FolderDetailView.as_view(), name='folder_detail'),
    path('folders/<int:parent_folder_pk>/create/', views.CreateSubfolderView.as_view(), name='create_subfolder'),
    path('folders/<int:pk>/delete/', views.DeleteFolderView.as_view(), name='delete_folder'),
]