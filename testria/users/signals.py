from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .tasks import send_confirmation_email_task


@receiver(post_save, sender=get_user_model())
def send_verification_email_after_registration(sender, instance, created, **kwargs):
    if created and not instance.is_verified:
        send_confirmation_email_task.delay(instance.pk)