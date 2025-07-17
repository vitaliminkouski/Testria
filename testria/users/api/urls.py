from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView
from . import views

app_name='users'

urlpatterns = [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),

    path('register/', views.UserRegisterAPIView.as_view(), name='api_register'),
    path('profile/', views.UserProfileAPIView.as_view(), name='api_profile'),
    path('view-profile/<str:username>/', views.OtherUserProfileAPIView.as_view(), name='api_view_profile'),

    path('password-reset/', views.PasswordResetRequestAPIView.as_view(), name='api_password_reset'),
    path('password-reset/confirm/', views.PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),

    path('resend-verification-email/', views.ResendVerificationEmailAPIView.as_view(), name='api_resend_verification_email'),
    path('verification/', views.VerifyEmailAPIView.as_view(), name='api_verify'),

]