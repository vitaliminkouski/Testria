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
    path('set/', views.SetListView.as_view(), name='set_list'),
    path('set/<int:set_id>/new-test-question/', views.create_test_question_view, name='create_test_question'),
    path('set/<int:pk>/edit/', views.EditSetView.as_view(), name='edit_set'),

    path('test/<int:set_id>/start/', views.start_test_view, name='start_test'),
    path('test/<int:session_id>/pass/', views.take_test_question_view, name='take_test_question'),
]