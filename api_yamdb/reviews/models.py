from django.core.validators import MaxValueValidator
from datetime import datetime
from django.db import models


class Category(models.Model):
    """Модель для категорий."""
    name = models.CharField(
        'Название категории',
        max_length=256,
        blank=False,
        null=False,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг имени группы',
        max_length=50,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Модель для Жанров."""
    name = models.CharField(
        'Название жанра',
        max_length=256,
        blank=False,
        null=False,
        unique=True,
    )
    slug = models.SlugField(
        'Слаг имени жанра',
        max_length=50,
        blank=False,
        null=False,
        unique=True,
    )

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель для произведений."""
    name = models.CharField(
        'Название произведения',
        max_length=500,
        blank=False,
        null=False,
    )
    year = models.IntegerField(
        'Год выпуска',
        blank=False,
        null=False,
        default=datetime.now().year,
        validators=[
            MaxValueValidator(
                int(datetime.now().year),
                message='Год выпуска не может быть больше текущего.'
            )
        ]
    )
    description = models.TextField(
        'Описание произведения'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=False,
        null=True,
        related_name='title',
        verbose_name='Категория произведения',
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
    )

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    """Модель для связи произведения и жанра."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.title} {self.genre}'
