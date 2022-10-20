from rest_framework import permissions
from users.models import User


class AdminSuperuser(permissions.BasePermission):
    """Дает доступ только админу и суперюзеру джанго."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == User.ADMIN
                or request.user.is_superuser)


class AnonymousUserReadOnly(permissions.BasePermission):
    """Дает доступ анониму только для чтения."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class AdminSuperuserAuthor(permissions.BasePermission):
    """Дает полный доступ к объекту только админу, суперюзеру и автору."""

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and request.user.is_superuser
                or request.user.role == User.ADMIN
                or request.user.role == User.MODERATOR
                or request.user == obj.author)
