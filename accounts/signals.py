from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.mail import send_mail
import random

from .models import User


@receiver(post_save, sender=User)
def send_activation_code(sender, instance, created, **kwargs):
    if not created:     
        return

    instance.activation_code = str(random.randint(100000, 999999))
    instance.code_created_at = timezone.now()
    instance.save(update_fields=["activation_code", "code_created_at"])

    send_mail(
        subject="Код подтверждения аккаунта",
        message=f"Ваш код подтверждения: {instance.activation_code}",
        from_email="noreply@example.com",
        recipient_list=[instance.email],
        fail_silently=False,
    )
