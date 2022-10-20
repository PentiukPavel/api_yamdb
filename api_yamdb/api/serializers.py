from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Genre, Title

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

    class Meta:
        model = Title
        fields = '__all__'
