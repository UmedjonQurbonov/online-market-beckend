from django.utils import timezone
import random
from django.core.mail import send_mail

def send_activation_code(user):
    code = str(random.randint(100000, 999999))
    user.activation_code = code
    user.code_created_at = timezone.now()
    user.save()

    subject = "Ваш код подтверждения"
    message = f"Привет, {user.username}!\n\nВаш код для активации аккаунта: {code}\nСрок действия кода — 10 минут."
    send_mail(subject, message, None, [user.email], fail_silently=False)
