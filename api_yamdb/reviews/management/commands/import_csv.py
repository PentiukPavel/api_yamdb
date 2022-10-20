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
    Comments
)
from users.models import User


class Command(BaseCommand):
    help = 'Импорт данных из файлов CSV.'

    def handle(self, *args, **kwargs):
        try:
            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'category.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    Category.objects.create(
                        id=line['id'],
                        name=line['name'],
                        slug=line['slug']
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'genre.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    Genre.objects.create(
                        id=line['id'],
                        name=line['name'],
                        slug=line['slug']
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'titles.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    Title.objects.create(
                        id=line['id'],
                        name=line['name'],
                        year=line['year'],
                        category=Category.objects.get(id=line['category']),
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'genre_title.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    GenreTitle.objects.create(
                        id=line['id'],
                        title_id=Title.objects.get(id=line['title_id']),
                        genre_id=Genre.objects.get(id=line['genre_id']),
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'users.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    User.objects.create(
                        id=line['id'],
                        username=line['username'],
                        email=line['email'],
                        role=line['role'],
                        bio=line['bio'],
                        first_name=line['first_name'],
                        last_name=line['last_name'],
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'review.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    Review.objects.create(
                        id=line['id'],
                        title_id=Title.objects.get(id=line['title_id']),
                        text=line['text'],
                        author=User.objects.get(id=line['author']),
                        score=line['score'],
                        pub_date=line['pub_date'],
                    )

            with open(
                os.path.join(
                    settings.BASE_DIR,
                    'static',
                    'data',
                    'comments.csv'
                ),
                encoding='utf-8'
            ) as data:
                for line in csv.DictReader(data):
                    Comments.objects.create(
                        id=line['id'],
                        review_id=Review.objects.get(id=line['title_id']),
                        text=line['text'],
                        author=User.objects.get(id=line['author']),
                        pub_date=line['pub_date'],
                    )
        except Exception as err:
            print(err)