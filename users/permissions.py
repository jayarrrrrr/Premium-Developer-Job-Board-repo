from rest_framework import permissions


class IsDeveloper(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        try:
            # normalize role and check
            return user.get_role() == 'developer' or getattr(user, 'is_staff', False)
        except Exception:
            return False


class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        try:
            return user.get_role() == 'employer' or getattr(user, 'is_staff', False)
        except Exception:
            return False


class IsPremiumUser(permissions.BasePermission):
    def has_permission(self, request, view):
        user = getattr(request, 'user', None)
        if not user or not getattr(user, 'is_authenticated', False):
            return False
        try:
            profile = user.get_or_create_profile()
            return bool(profile.is_premium)
        except Exception:
            return False
