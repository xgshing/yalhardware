from django.conf import settings
from rest_framework.permissions import BasePermission


class IsAdminUser(BasePermission):
    """Allow staff users, with an optional test bypass for admin APIs."""

    def has_permission(self, request, view):
        if bool(getattr(settings, "TEST_BYPASS_ADMIN_AUTH", False)):
            return True
        return bool(
            request.user and request.user.is_authenticated and request.user.is_staff
        )
