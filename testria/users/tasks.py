from celery import shared_task
from testria import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from testria.private_settings import EMAIL_HOST_PASSWORD

@shared_task
def send_confirmation_email_task(user_id):
    try:
        user=get_user_model().objects.get(pk=user_id)
    except user.DoesNotExist:
        print(f"User with id {user_id} does not exist. Verification email not sent")
        return

    uid=urlsafe_base64_encode(force_bytes(user.pk))
    token=default_token_generator.make_token(user)

    protocol='http'
    confirm_url=f"{protocol}://{settings.IP}/users/verification/{uid}/{token}/"

    html_message=render_to_string('users/email_confirmation.html', {
        'user': user,
        'confirm_url': confirm_url,
    })

    plain_message=strip_tags(html_message)

    try:
        send_mail(
            'Confirm your email',
            plain_message,
            EMAIL_HOST_PASSWORD,
            [user.email],
            fail_silently=False,
            html_message=html_message)
        print(f"Confirmation email sent to {user.email}")
    except Exception as e:
        print(f"Failed to send confirmation email to {user.email}: {e}")



