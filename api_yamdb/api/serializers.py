from django.contrib.auth import get_user_model
from rest_framework import serializers
from reviews.models import Category, Genre, GenreTitle, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role',)
        extra_kwargs = {'username': {'required': True},
                        'email': {'required': True}}


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


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор Произведений."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'

    def create(self, validated_data):
        category = validated_data.pop('category')
        title_category, status = Category.objects.get_or_create(**category)
        genres = validated_data.pop('genre')
        title = Title.objects.create(category=title_category, **validated_data)
        for genre in genres:
            current_genre, status = Genre.objects.get_or_create(**genres)
            GenreTitle.objects.create(genre=current_genre, title=title)
        return title
