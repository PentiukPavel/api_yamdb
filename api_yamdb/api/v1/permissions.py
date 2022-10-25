from rest_framework import permissions


class AdminSuperuserOnly(permissions.BasePermission):
    """Дает доступ только админу и суперюзеру джанго.

    Доступ и к списку и объектам.
    """

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_superuser)


class AdminSuperuserOrReadOnly(permissions.BasePermission):
    """Дает доступ только админу и суперюзеру джанго.

    Остальным доступ только для чтения.
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_superuser)


class AdminSuperuserModeratorAuthorOrReadOnly(permissions.BasePermission):
    """Дает полный доступ к объекту только админу, суперюзеру и автору.

    Доступ к списку и к объекту для чтения всем пользователям.
    Доступ к редактированию перечисленным пользователям.
    У объекта должно быть поле author
    """

    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated
                and (request.user.is_superuser
                     or request.user.is_admin
                     or request.user.is_moderator
                     or request.user == obj.author))
