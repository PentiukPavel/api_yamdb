from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомизированная модель пользователя."""

    USER = 1
    MODERATOR = 2
    ADMIN = 3

    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.PositiveSmallIntegerField(
        choices=ROLE_CHOICES,
        default=USER,
        blank=True,
        null=False,
    )
