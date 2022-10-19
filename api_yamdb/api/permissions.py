from rest_framework import permissions
from users.models import User


class AdminPermission(permissions.BasePermission):
    """Разрешает просмотр и редактирование объектов только админу."""

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.role == User.ADMIN
                or request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        return (request.user.role == User.ADMIN or request.user.is_superuser)
