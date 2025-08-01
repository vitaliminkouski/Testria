from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('folders/create/', views.CreateFolderView.as_view(), name='create_folder'),
    path('folders/<int:pk>/', views.FolderDetailView.as_view(), name='folder_detail'),
    path('folders/<int:pk>/edit/', views.EditFolderView.as_view(), name='edit_folder'),
    path('folders/<int:pk>/delete/', views.DeleteFolderView.as_view(), name='delete_folder'),
    path('set/create/<int:folder_pk>/', views.CreateSetView.as_view(), name='create_set'),
    path('set/<int:pk>/delete/', views.DeleteSetView.as_view(), name='delete_set'),
    path('set/', views.SetListView.as_view(), name='set_list')
]