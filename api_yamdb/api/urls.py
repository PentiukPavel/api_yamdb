from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

user_create = views.UserRegisterViewSet.as_view(
    {'post': 'create', })
token_create = views.TokenCreateViewSet.as_view(
    {'post': 'create', })
current_user_get_update = views.CurrentUserViewSet.as_view(
    {'get': 'retrieve',
     'patch': 'partial_update'},)


v1_router = DefaultRouter()
v1_router.register(r'users', views.UserViewSet, basename='users')
v1_router.register(r'categories', views.CategoryViewSet, basename='categories')
v1_router.register(r'genres', views.GenreViewSet, basename='genres')
v1_router.register(r'titles', views.TitleViewSet, basename='titles')
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    views.ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    views.CommentViewSet,
    basename='comments'
)

urlpatterns = [
    path('v1/users/me/',
         current_user_get_update,
         name='me',
         ),
    path('v1/auth/signup/',
         user_create,
         name='signup',),
    path('v1/auth/token/',
         token_create,
         name='token',),
    path('v1/', include(v1_router.urls)),
]
