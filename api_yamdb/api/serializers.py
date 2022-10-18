from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор кода подтверждения."""

    username = serializers.CharField(
        max_length=30,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )
