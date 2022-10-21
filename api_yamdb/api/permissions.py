from rest_framework import permissions
from users.models import User as UserModel


class AdminSuperuserOnly(permissions.BasePermission):
    """Дает доступ только админу и суперюзеру джанго.

    Доступ и к списку и объектам.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == UserModel.ADMIN
                or request.user.is_superuser)


class AnonymousUserReadOnly(permissions.BasePermission):
    """Дает доступ анониму только для чтения.

    Доступ и к списку и объектам.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AdminSuperuserModeratorAuthorOnly(permissions.BasePermission):
    """Дает полный доступ к объекту только админу, суперюзеру и автору.

    Доступ к списку и к объекту для чтения всем пользователям.
    Доступ к редактированию перечисленным пользователям.
    У объекта должно быть поле author
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user.is_superuser
                    or request.user.role == UserModel.ADMIN
                    or request.user.role == UserModel.MODERATOR
                    or request.user == obj.author))


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Дает доступ к объекту только владельцу.

    Доступ к списку и к объекту для чтения всем пользователям.
    Доступ к редактированию только владельцу.
    """

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or (request.user.is_authenticated
                    and request.user == obj.author))
