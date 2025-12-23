from rest_framework.permissions import BasePermission

class IsAdminRole(BasePermission):
    message = "Admin access required."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Check role from LoginModule
        return (
            hasattr(request.user, 'loginmodule') and
            request.user.loginmodule.role == 'ADMIN'
        )
