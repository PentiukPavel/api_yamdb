from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

user_create = views.UserCreateViewSet.as_view({'post': 'create', })
token_create = views.TokenCreateViewSet.as_view({'post': 'create', })

v1_router = DefaultRouter()
v1_router.register('users', views.UserViewSet, basename='users')
v1_router.register(r'categories', views.CategoryViewSet, basename='categories')
v1_router.register(r'genres', views.GenreViewSet, basename='genres')
v1_router.register(r'titles', views.TitleViewSet, basename='titles')

urlpatterns = [
    path('v1/auth/signup/',
         user_create,
         name='signup',),
    path('v1/auth/token/',
         token_create,
         name='token',),
    path('v1/', include(v1_router.urls)),
]
