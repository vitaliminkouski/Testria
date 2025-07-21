from django.contrib.auth import get_user_model, login, logout
from django.core.serializers import serialize
from django.middleware.csrf import get_token
from django.shortcuts import redirect
from django.urls import reverse_lazy
from rest_framework import generics, status, views
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.api.serializers import UserRegisterSerializer, UserSerializer, OtherUserSerializer, \
    PasswordResetRequestSerializer, PasswordResetConfirmSerializer, EmailConfirmationSerializer, \
    PasswordChangeSerializer, SessionLoginSerializer, CustomTokenObtainPairSerializer
from users.tasks import send_password_reset_email_task
from users.user_services import UserServices
from users.custom_user_errors import FollowOnYourselfError, AlreadyFollowedOnUserError


class UserRegisterAPIView(generics.CreateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserRegisterSerializer

class UserProfileAPIView(generics.RetrieveUpdateAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, ]

    def get_object(self):
        return self.request.user

class OtherUserProfileAPIView(generics.RetrieveAPIView):
    queryset = get_user_model().objects.all()
    serializer_class = OtherUserSerializer
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, ]

    def retrieve(self, request, *args, **kwargs):
        if self.request.user.is_authenticated and \
            self.request.user.username==self.kwargs.get('username'):
            return redirect(reverse_lazy('api_users:api_profile'))
        return super().retrieve(request, *args, **kwargs)

class PasswordResetRequestAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email=serializer.validated_data['email']
        user = get_object_or_404(get_user_model(), email=email)

        send_password_reset_email_task.delay(user.pk)

        return Response({"details": "Password reset email has been sent"},
                        status=status.HTTP_200_OK)

class PasswordResetConfirmAPIView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user=serializer.save()
        return Response(
            {"detail": "Password has been reset successfully."},
            status=status.HTTP_200_OK
        )

class ResendVerificationEmailAPIView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if UserServices.resend_verification_email(request):
            return Response({"detail": "Verification email has been sent to your email address"},
                            status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Your email is already verified"},
                            status=status.HTTP_400_BAD_REQUEST)

class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = EmailConfirmationSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            uid = serializer.validated_data['uid']
            token = serializer.validated_data['token']
            UserServices.verify_email(uid, token)
            return Response({"detail": "Your email has been verified successfully"})
        except Exception as e:
            return Response({"error": str(e)})

class PasswordChangeAPIView(generics.GenericAPIView):
    serializer_class = PasswordChangeSerializer
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"detail": "Password changed successfully"},
                        status=status.HTTP_200_OK)

class SessionLoginAPIView(generics.GenericAPIView):
    serializer_class = SessionLoginSerializer
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer=self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user=serializer.validated_data['user']
        login(request, user)
        return Response({"detail": "Logged in successfully."}, status=status.HTTP_200_OK)

class SessionLogoutAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"detail": "Logged out successfully."}, status=status.HTTP_200_OK)



class FollowAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, username, *args, **kwargs):
        try:
            UserServices.follow_on(request, username)
            return Response({"detail": f"You've succesfully followed on {username}"})
        except(AlreadyFollowedOnUserError, FollowOnYourselfError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UnfollowAPIView(views.APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, username, *args, **kwargs):
        try:
            UserServices.unfollow_on(request, username)
            return Response({"detail": f"You stop following on {username}"})
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListFollowingAPIView(generics.ListAPIView):
    serializer_class = OtherUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            username=self.kwargs.get('username')
        except:
            return Response({"error": "username not provided"},
                            status=status.HTTP_400_BAD_REQUEST)
        target_user=get_object_or_404(get_user_model(), username=username)
        return target_user.following.all()


class ListFollowersAPIView(generics.ListAPIView):
    serializer_class = OtherUserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        try:
            username = self.kwargs.get('username')
        except:
            return Response({"error": "username not provided"},
                            status=status.HTTP_400_BAD_REQUEST)
        target_user = get_object_or_404(get_user_model(), username=username)
        return target_user.followers.all()

class CustomTokenObtainPairView(TokenObtainPairView):
    _serializer_class = CustomTokenObtainPairSerializer

    def get_serializer(self, *args, **kwargs):
        return CustomTokenObtainPairSerializer(data=self.request.data)
