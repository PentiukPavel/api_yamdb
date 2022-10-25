from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, permissions, viewsets, serializers
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Title, Review
from users.models import User as UserModel

from ..utils.auth_utils import send_confirmation_code
from .filters import TtileFilter
from .permissions import (AdminSuperuserModeratorAuthorOrReadOnly,
                          AdminSuperuserOnly, AdminSuperuserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          ConfirmationCodeSerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializerGet,
                          TitleSerializerPost, UserRegisterSerializer,
                          UserSerializer)

User = get_user_model()


class UserRegisterViewSet(viewsets.GenericViewSet):
    """Вьюсет для самостоятельной регистрации пользователей.

    После создания отправляет email с кодом подтверждения.
    """

    serializer_class = UserRegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
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
    """Вьюсет для получения и обновления информации о пользователях."""

    queryset = User.objects.all().order_by('date_joined')
    serializer_class = UserSerializer
    permission_classes = (AdminSuperuserOnly, )
    filter_backends = (filters.SearchFilter, )
    lookup_field = 'username'
    search_fields = ('username',)

    @action(detail=False,
            methods=['get', 'patch'],
            url_path='me',
            url_name='me',
            permission_classes=(permissions.IsAuthenticated,))
    def get_patch_current_user_data(self, request):
        """Метод для получения и обновления информации о текущем юзере."""
        if request.method == 'PATCH':
            serializer = self.serializer_class(
                request.user, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            if request.user.role == UserModel.ADMIN:
                serializer.save()
            else:
                serializer.save(role=request.user.role)

        if request.method == 'GET':
            serializer = self.serializer_class(request.user)

        return Response(serializer.data, status=HTTPStatus.OK)


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
    permission_classes = (AdminSuperuserOrReadOnly,)


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
    permission_classes = (AdminSuperuserOrReadOnly,)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    queryset = Title.objects.annotate(rating=Avg('reviews__score')).all()
    pagination_class = LimitOffsetPagination
    filterset_class = TtileFilter
    filterset_fields = ('name', 'year', 'category', 'genre',)
    permission_classes = (AdminSuperuserOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TitleSerializerGet

        return TitleSerializerPost


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для комментариев к произведениям."""

    serializer_class = CommentSerializer
    permission_classes = (AdminSuperuserModeratorAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Возвращает комментарии к отзывам."""
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(Review, id=review_id, title=title)

        return review.comments.all()

    def perform_create(self, serializer):
        """Добавление автора комментария и отзыв."""
        title_id = self.kwargs.get('title_id')
        review_id = self.kwargs.get('review_id')

        title = get_object_or_404(Title, id=title_id)
        review = get_object_or_404(Review, id=review_id, title=title)

        serializer.save(author=self.request.user, review=review)


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отзывов к произведениям."""

    serializer_class = ReviewSerializer
    permission_classes = (AdminSuperuserModeratorAuthorOrReadOnly,)
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        """Возвращает отзывы к произведению."""
        title_id = self.kwargs.get('title_id')

        title = get_object_or_404(Title, id=title_id)

        return title.reviews.all()

    def perform_create(self, serializer):
        """Добавление автора отзыва и произведения."""
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)

        if title.reviews.filter(author=self.request.user).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на это произведение')

        serializer.save(author=self.request.user, title=title)
