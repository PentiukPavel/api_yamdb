import os
import csv

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import (
    Category,
    Genre,
    GenreTitle,
    Title,
    Review,
    Comment
)
from users.models import User


class Command(BaseCommand):
    help = 'Импорт данных из файлов CSV.'

    def handle(self, *args, **kwargs):

        name_models = {
            'category': Category,
            'genre': Genre,
            'titles': Title,
            'users': User,
            'review': Review,
            'comments': Comment,
            'genre_title': GenreTitle,
        }

        for name, model in name_models.items():
            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    f'{name}.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    i = {}
                    for key, value in line.items():
                        if key == 'category':
                            i[key] = name_models[key].objects.get(id=value)
                        elif key == 'author':
                            i[key] = User.objects.get(id=value)
                        else:
                            i[key] = value
                    model.objects.create(**i)
