from rest_framework.permissions import BasePermission, SAFE_METHODS


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return True
        return request.user.is_authenticated


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
