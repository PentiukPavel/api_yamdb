from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError
from rest_framework import serializers
from rest_framework.validators import ValidationError
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя при самостоятельное регистрации.

    Позволяет создать пользователя только с разрешенными полями.
    """

    def create(self, validated_data):
        try:
            instance, _ = self.Meta.model.objects.get_or_create(
                **validated_data)
        except IntegrityError as e:
            raise ValidationError(e) from e
        return instance

    class Meta:
        model = User
        fields = ('username', 'email',)
        extra_kwargs = {
            'username': {
                'validators': [],
            },
            'email': {
                'validators': [],
            },
        }

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Выберите другой юзернейм')
        return username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)


class ConfirmationCodeSerializer(serializers.Serializer):
    """Сериализатор кода подтверждения."""

    username = serializers.CharField(
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=150,
        required=True
    )


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    """Сериалайзер категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)
        lookup_field = 'slug'


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    """Сериалайзер жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = ('slug')


class TitleSerializerPost(serializers.ModelSerializer):
    """Сериализатор для получения Произведений."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )

    class Meta:
        model = Title
        fields = '__all__'


class TitleSerializerGet(serializers.ModelSerializer):
    """Сериализатор для вывода Произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('review',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для вывода отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
