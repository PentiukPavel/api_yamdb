from django.core.validators import MinValueValidator, MaxValueValidator
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


class Review(models.Model):
    """Модель отзывов."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение',
    )
    text = models.TextField(
        'Текст отзыва',
        blank=False,
        null=False,
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор отзыва',
    )
    score = models.IntegerField(
        'Оценка',
        blank=False,
        null=False,
        validators=[
            MinValueValidator(
                1,
                message='Оценка не может быть меньше 1.'
            ),
            MaxValueValidator(
                10,
                message='Оценка не может быть больше 10.'
            ),
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return f'{self.title} {self.author} {self.score}'

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


class Comment(models.Model):
    """Модель комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Отзыв',
    )
    text = models.TextField(
        'Текст комментария',
        blank=False,
        null=False,
    )
    author = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    def __str__(self):
        return f'{self.review} {self.author} {self.text}'
