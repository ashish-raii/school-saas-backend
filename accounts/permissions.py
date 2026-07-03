from rest_framework.permissions import BasePermission

class IsOrganizationAdmin(BasePermission):
    message = "Only organization admins can update these details."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "ORG_ADMIN"
        )
class IsEmployee(BasePermission):
    message = "Only Employee/Teacher can update these details."
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == "EMPLOYEE"
        )
        
