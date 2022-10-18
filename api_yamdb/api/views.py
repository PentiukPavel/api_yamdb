from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from .exceptions import ConfirmationCodeInvalidException
from .serializers import ConfirmationCodeSerializer, UserSerializer
from .utils.auth_utils import send_confirmation_code

User = get_user_model()


class UserCreateViewSet(viewsets.GenericViewSet):
    """Вьюсет для создания пользователей.

    После создания отправляет email с кодом подтверждения.
    """

    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(user.email, confirmation_code)
        return Response(serializer.data, status=HTTPStatus.OK)


class TokenCreateViewSet(viewsets.GenericViewSet):
    """Вьюсет для создания JWT токена.

    Токен будет создан если код подтверждения полученный по email валиден.
    """

    serializer_class = ConfirmationCodeSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data.get(
            'confirmation_code')
        user = get_object_or_404(User, username=username)

        if not default_token_generator.check_token(
                user, confirmation_code):
            raise ConfirmationCodeInvalidException(
                'Время действия токена истекло или токен неверен')
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
