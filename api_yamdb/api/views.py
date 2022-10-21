from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Title

from .exceptions import EmailException
from .filters import MyFilterBackend
from .permissions import AdminSuperuserOnly, AnonymousUserReadOnly
from .serializers import (CategorySerializer, ConfirmationCodeSerializer,
                          GenreSerializer, TitleSerializerGet,
                          TitleSerializerPost, UserRegisterSerializer,
                          UserSerializer)
from .utils.auth_utils import send_confirmation_code

User = get_user_model()


class CurrentUserViewSet(viewsets.ViewSet):
    """Вьюсет для получения и обновления информации о текущем юзере."""

    serializer_class = UserSerializer

    def retrieve(self, request, pk=None):
        serializer = self.serializer_class(request.user)
        return Response(serializer.data)

    def partial_update(self, request, pk=None):
        request_data = request.data
        serializer = self.serializer_class(
            request.user, data=request_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=request.user.role)
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
        try:
            send_confirmation_code(user, confirmation_code)
        except Exception as e:
            user.delete()
            raise EmailException(
                'Не удалось отправить письмо с кодом подтверждения. '
                'Пользователь не создан.'
                f'Причина: {e}')
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
    permission_classes = (AdminSuperuserOnly, )
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'username'
    search_fields = ('username',)


class CategoryViewSet(viewsets.ModelViewSet):
    """Вьюсет для Категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AnonymousUserReadOnly | AdminSuperuserOnly,)


class GenreViewSet(viewsets.ModelViewSet):
    """Вьюсет для Жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AnonymousUserReadOnly | AdminSuperuserOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.all()
    pagination_class = LimitOffsetPagination
    filter_backends = [MyFilterBackend]
    filterset_fields = ('name', 'year', 'category', 'genre,')
    permission_classes = (AnonymousUserReadOnly | AdminSuperuserOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return TitleSerializerGet
        if self.action == 'retrieve':
            return TitleSerializerGet
        return TitleSerializerPost
