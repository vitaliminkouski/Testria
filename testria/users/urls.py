from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordChangeDoneView

app_name = 'users'
urlpatterns = [
    path('register/', views.RegisterUserView.as_view(), name='register'),
    path('login/', views.LoginUserView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('password-reset/', PasswordResetView.as_view(
        template_name='users/password_reset_form.html',
        email_template_name='users/password_reset_email.html',
        success_url=reverse_lazy('users:password_reset_done'),
    ), name='password_reset'),

    path('password-reset/done/',
         PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/',
         PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
         success_url=reverse_lazy('users:password_reset_complete')),
         name='password_reset_confirm'),
    path('password-reset/complete/',
         PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'),
         name='password_reset_complete'),

    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('password-change-done/',
         PasswordChangeDoneView.as_view(template_name='users/password_change_done.html'),
         name='password_change_done'),
    path('verification/<uidb64>/<token>/', views.verify_email_view, name='verification'),
    path('resend-verification/', views.resend_verification_email_view, name='resend_verification'),
    path('view-profile/<str:username>/', views.OtherUserView.as_view(), name='view_profile'),
    path('follow/<str:username>/', views.follow_view, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_view, name='unfollow'),
    path('followers/<str:username>/', views.ListFollowersView.as_view(), name='followers'),
    path('following/<str:username>/', views.ListFollowingView.as_view(), name='following'),

]