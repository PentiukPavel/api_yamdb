from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Title
from users.models import User as UserModel

from .filters import MyFilterBackend
from .permissions import (AdminSuperuserModeratorAuthorOnly,
                          AdminSuperuserOnly, AnonymousUserReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializerGet,
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
        serializer = self.serializer_class(
            request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if request.user.role == UserModel.ADMIN:
            serializer.save()
        else:
            serializer.save(role=request.user.role)
        return Response(serializer.data, status=HTTPStatus.OK)


class UserRegisterViewSet(viewsets.GenericViewSet):
    """Вьюсет для самостоятельной регистрации пользователей.

    После создания отправляет email с кодом подтверждения.
    """

    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        username = request.data.get('username')
        email = request.data.get('email')

        if User.objects.filter(username=username, email=email).exists():
            user = User.objects.get(username=username, email=email)
            serializer = self.get_serializer(user)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()

        confirmation_code = default_token_generator.make_token(user)
        send_confirmation_code(user, confirmation_code)

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


class CategoryViewSet(mixins.CreateModelMixin,
                      mixins.DestroyModelMixin,
                      mixins.ListModelMixin,
                      viewsets.GenericViewSet):
    """Вьюсет для Категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    pagination_class = LimitOffsetPagination
    permission_classes = (AnonymousUserReadOnly | AdminSuperuserOnly,)


class GenreViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
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
    filterset_fields = ('name', 'year', 'category', 'genre',)
    permission_classes = (AnonymousUserReadOnly | AdminSuperuserOnly,)

    def get_serializer_class(self):
        if self.action == 'list':
            return TitleSerializerGet
        if self.action == 'retrieve':
            return TitleSerializerGet
        return TitleSerializerPost


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к произведениям."""

    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminSuperuserModeratorAuthorOnly
    )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = title.reviews.get(id=review_id)

        return review.comments.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = title.reviews.get(id=review_id)

        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов к произведениям."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        AdminSuperuserModeratorAuthorOnly,
    )
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')

        title = get_object_or_404(Title, id=title_id)
        return title.reviews.all()

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')

        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)
