from rest_framework import permissions
from aristotle_mdr_api.token_auth.permissions import TokenPermissions

class IsSuperuserOrReadOnly(permissions.BasePermission):
    """
    Allows access only to super users.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user and
            request.user.is_authenticated() and
            request.user.is_superuser
        )
