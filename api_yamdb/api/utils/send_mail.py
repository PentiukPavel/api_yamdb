from django.core.mail import send_mail


def email_confirmation_code(user_email, confirmation_code):
    """Отправляет почту через выбранный email backend."""
    send_mail(
        subject='Код подтверждения для получения токена',
        message=confirmation_code,
        from_email='yamdb@test.com',
        recipient_list=[user_email, ],
        fail_silently=False,)
