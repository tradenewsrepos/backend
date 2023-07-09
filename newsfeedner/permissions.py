from rest_framework.permissions import BasePermission


class ApproverPermissions(BasePermission):
    allowed_user_roles = ["annotation approver", "admin", "annotator"]

    def has_permission(self, request, view):
        try:
            role = request.user.role
        except AttributeError:
            return None
        is_allowed_user: bool = str(role) in self.allowed_user_roles
        return is_allowed_user
