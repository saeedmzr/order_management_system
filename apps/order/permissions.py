from rest_framework.permissions import BasePermission

class IsOrderOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.customer == request.user or request.user.is_staff