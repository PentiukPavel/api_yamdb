from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

User = get_user_model()


def send_confirmation_code(user: User, confirmation_code: str):
    """Отправляет почту через выбранный email backend."""
    send_mail(
        subject=f'Код подтверждения Yamdb для пользователя {user.username}',
        message=confirmation_code,
        from_email=settings.YAMDB_EMAIL,
        recipient_list=[user.email, ],
        fail_silently=False,)
