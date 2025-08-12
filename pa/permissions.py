from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import Plan, Profile


class RolePermission(BasePermission):
    """Permissions basées sur le rôle du profil."""

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        role = getattr(user.profile, "role", None)
        if role == Profile.Role.SUPER_ADMIN:
            return True
        if role == Profile.Role.PILOTE_PROCESSUS:
            return True
        if role == Profile.Role.PILOTE:
            return True
        if role == Profile.Role.UTILISATEUR:
            return request.method in SAFE_METHODS
        return False

    def has_object_permission(self, request, view, obj):
        user = request.user
        role = user.profile.role
        if role in (Profile.Role.SUPER_ADMIN, Profile.Role.PILOTE_PROCESSUS):
            return True
        allowed = user.profile.plans_autorises.all()
        plan = obj if isinstance(obj, Plan) else obj.plan
        if role == Profile.Role.PILOTE:
            return plan in allowed
        if role == Profile.Role.UTILISATEUR and request.method in SAFE_METHODS:
            return plan in allowed
        return False
