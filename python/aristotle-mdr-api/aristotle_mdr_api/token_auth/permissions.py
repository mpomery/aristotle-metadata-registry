from rest_framework.permissions import SAFE_METHODS
from restfw_composed_permissions.base import BaseComposedPermision, BasePermissionComponent, And, Or
from restfw_composed_permissions.generic.components import AllowOnlyAuthenticated


class TokenPermissions(BasePermissionComponent):

    permission_key = 'default'

    def has_permission(self, permission, request, view):

        token = request.auth

        # request.auth will be None when using any other default authentication class
        if token is not None:

            if hasattr(view, 'permission_key'):
                permission_key = getattr(view, 'permission_key')
            else:
                permission_key = self.permission_key

            hasread = False
            haswrite = False

            perms = token.permissions

            if permission_key in perms.keys():
                perm = perms[permission_key]

                if 'read' in perm:
                    hasread = perm['read']

                if 'write' in perm:
                    haswrite = perm['write']

        else:
            # Default for non token auths
            hasread = True
            haswrite = False

        if request.method in SAFE_METHODS and hasread:
            return True

        if request.method not in SAFE_METHODS and haswrite:
            return True

        return False


class AristotlePermissions(BaseComposedPermision):

    global_permission_set = (lambda s: And(AllowOnlyAuthenticated, TokenPermissions))
