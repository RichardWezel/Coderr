from rest_framework import permissions


class UpdatingUserIsProfileUser(permissions.BasePermission):
    """
    Permission class to ensure that only the owner of a profile can update it.
    """

    def has_object_permission(self, request, view, obj):
        # Allow safe methods (GET, HEAD, OPTIONS) for any user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Allow updates only if the requesting user is the owner of the profile
        return obj.user == request.user
