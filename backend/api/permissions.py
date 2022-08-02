from rest_framework.permissions import SAFE_METHODS, BasePermission


class UserPermission(BasePermission):

    def has_permission(self, request, view):
        if view.action in ['list', 'create']:
            return True
        return request.user.is_authenticated


class IsReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author)
