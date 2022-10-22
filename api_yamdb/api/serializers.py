from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя при самостоятельное регистрации.

    Позволяет создать пользователя только с разрешенными полями.
    """
    class Meta:
        model = User
        fields = ('username', 'email',)
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True}}

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Выберите другой юзернейм')
        return username


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True}}

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Выберите другой юзернейм')
        return username


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
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    """Сериалайзер жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)
        lookup_field = ('slug')
        extra_kwargs = {
            'url': {'lookup_field': 'slug'}
        }


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

    def create(self, validated_data):
        """Проверка на наличие отзыва от пользователя."""
        user = self.context['request'].user
        title = validated_data.get('title')

        if Review.objects.filter(author=user, title=title).exists():
            raise serializers.ValidationError(
                'Вы уже оставили отзыв на этот произведение')

        return Review.objects.create(**validated_data)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date',)
        read_only_fields = ('title',)
