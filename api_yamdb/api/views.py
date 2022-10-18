from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre

from .exceptions import TokenInvalidException
from .serializers import (
    ConfirmationCodeSerializer,
    CategorySerializer,
    GenreSerializer,
    UserSerializer,
)
from .utils.send_mail import email_confirmation_code

User = get_user_model()


class UserCreateViewSet(mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """Вьюсет для создания пользователей.

    После создания отправляет email с кодом подтверждения.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user, _ = User.objects.get_or_create(**serializer.validated_data)
            confirmation_code = default_token_generator.make_token(user)
            email_confirmation_code(user.email, confirmation_code)
            return Response(serializer.data, status=HTTPStatus.OK)


class CreateTokenViewSet(mixins.CreateModelMixin,
                         viewsets.GenericViewSet):
    """Вьюсет для создания JWT токена.

    Токен будет создан если код подтверждения полученный по email валиден.
    """

    queryset = User.objects.all()
    serializer_class = ConfirmationCodeSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            username = serializer.validated_data.get('username')
            confirmation_code = serializer.validated_data.get(
                'confirmation_code')
            user = get_object_or_404(User, username=username)
            if not default_token_generator.check_token(user,
                                                       confirmation_code):
                raise TokenInvalidException(
                    'Время действия токена истекло или токен неверен')
            return Response(
                {'token': str(AccessToken.for_user(user))},
                status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для Категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fileds = ('name',)
    pagination_class = (LimitOffsetPagination,)


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для Жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fileds = ('name',)
    pagination_class = (LimitOffsetPagination,)
