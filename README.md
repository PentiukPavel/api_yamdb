# api_yamdb

## Описание

Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории. Например, книги, фильмы, музыка.


## Технологии

- Python 3.8
- Django 2.2.16
- Django REST Framework 3.12.4
- Simple JWT 5.2.1
- Redoc 0.9.8


## Как запустить проект

Склонируйте репозиторий на локальную машину и перейдите в папку с проектом

```
git clone git@github.com:PentiukPavel/api_yamdb.git
cd api_yamdb
```

Создайте и активируйте виртуальное окружение

```
python -m venv venv

# Windows
source venv/Scripts/activate

# MacOS
source venv/bin/activate
```

Установите зависимости из файла requirements.txt

```
pip install -r requirements.txt
```

Выполните миграции

```
python manage.py migrate
```

Запустите проект! 

```
python manage.py runserver
```

## Примеры запросов к API

- Создание пользователя

```
POST /api/v1/auth/signup/

{
    "email": "string",
    "username": "string",
    "password": "string",
}
```

- Получение JWT-токена

```
POST /api/v1/auth/token/

{
    "confirmation_code": "string",
    "username": "string",
    "password": "string",
}
```

- Получение списка всех произведений, ревью и комментариев

```
GET /api/v1/titles/
GET /api/v1/titles/{title_id}/reviews/
GET /api/v1/titles/{title_id}/reviews/{review_id}/comments/
```

## Авторы проекта

- Пеньтюк Павел [Github](https://github.com/PentiukPavel)
- Нурмухамбетов Амир [Github](https://github.com/Hereugo)
- Вячеслав Александр [Github](https://github.com/valexandro)