from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrDirectorOrReadOnly(BasePermission):
    message = "Solo administradores y directores pueden modificar jugadores."

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        return self._has_write_permission(request.user)

    def _has_write_permission(self, user):
        if not user or not user.is_authenticated:
            return False
        if getattr(user, "is_staff", False):
            return True
        if hasattr(user, "user_roles"):
            return user.user_roles.filter(role__name__in=["admin", "director"]).exists()
        return False
