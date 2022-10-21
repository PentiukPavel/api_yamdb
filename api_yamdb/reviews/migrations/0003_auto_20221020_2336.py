# Generated by Django 2.2.16 on 2022-10-20 23:36

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_title_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='genre',
            name='name',
            field=models.CharField(max_length=256, verbose_name='Название жанра'),
        ),
        migrations.AlterField(
            model_name='genretitle',
            name='genre',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genre', to='reviews.Genre'),
        ),
        migrations.AlterField(
            model_name='genretitle',
            name='title',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='title', to='reviews.Title'),
        ),
        migrations.AlterField(
            model_name='title',
            name='rating',
            field=models.IntegerField(null=True, validators=[django.core.validators.MaxValueValidator(10, message='Рейтинг не может быть больше 10.'), django.core.validators.MaxValueValidator(0, message='Рейтинг не может быть меньше 0.')], verbose_name='Рейтинг произведения'),
        ),
    ]
