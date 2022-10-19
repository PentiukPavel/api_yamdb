from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre

from .permissions import AdminPermission
from .serializers import (CategorySerializer, ConfirmationCodeSerializer,
                          GenreSerializer, UserRegisterSerializer,
                          UserSerializer)
from .utils.auth_utils import send_confirmation_code

User = get_user_model()


class CurrentUserViewSet(viewsets.ViewSet):
    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.OK)


class UserRegisterViewSet(viewsets.GenericViewSet):
    """Вьюсет для самостоятельной регистрации пользователей.

    После создания отправляет email с кодом подтверждения.
    """

    serializer_class = UserRegisterSerializer
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
            return Response(
                {'error': 'Код подтверждения неверен или устарел'},
                status=HTTPStatus.BAD_REQUEST)
        return Response(
            {'token': str(AccessToken.for_user(user))},
            status=HTTPStatus.OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminPermission, )
    lookup_field = 'username'


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
