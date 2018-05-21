from rest_framework import permissions

class TokenPermissions(permissions.BasePermission):

    permission_key = 'default'

    def is_authenticated(self, request):
        return request.user and request.user.is_authenticated

    def has_permission(self, request, view):

        authenticated = self.is_authenticated(request)

        if not authenticated:
            return False

        if hasattr(view, 'permission_key'):
            self.permission_key = getattr(view, 'permission_key')

        token = request.auth

        # request.auth will be None when using any other default authentication class
        if token is not None:
            perms = token.permissions

            if self.permission_key in perms.keys():
                perm = perms[self.permission_key]

                if 'read' in perm:
                    hasread = perm['read']
                else:
                    hasread = False

                if 'write' in perm:
                    haswrite = perm['write']
                else:
                    haswrite = False

        else:
            # Default for non token auths
            hasread = True
            haswrite = request.user.is_superuser

        if request.method in permissions.SAFE_METHODS and hasread:
            return True

        if request.method not in permissions.SAFE_METHODS and haswrite:
            return True

        return False
