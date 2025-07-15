from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_str, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode

from .custom_user_errors import *
from .tasks import send_confirmation_email_task


class UserServices:
    @staticmethod
    def unfollow_on(request, username):
        target_user = get_object_or_404(get_user_model(), username=username)
        if request.user.is_following(target_user):
            request.user.following.remove(target_user)

    @staticmethod
    def follow_on(request, username):
        if request.user.username == username:
            raise FollowOnYourselfError("You can't follow on yourself")
        target_user = get_object_or_404(get_user_model(), username=username)
        if request.user.is_following(target_user):
            raise AlreadyFollowedOnUserError(f"You're already followed on {username}")
        else:
            request.user.following.add(target_user)

    @staticmethod
    def verify_email(uidb64, token):
        User = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist, DjangoUnicodeDecodeError):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_verified = True
            user.save()
            return user
        else:
            raise ConfirmationLinkError('The confirmation link is invalid or has expired')

    @staticmethod
    def resend_verification_email(request):
        if not request.user.is_verified:
            send_confirmation_email_task.delay(request.user.pk)
            return True
        else:
            return False