from rest_framework import permissions

class IsUserOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return True if obj.user == request.user else False

