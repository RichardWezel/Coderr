from rest_framework import permissions

class isOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class isBusinessUser(permissions.BasePermission):
    """
    Custom permission to only allow business users to create, update, or delete offers.
    """

    message = "Only User with type 'business' can post a new offer!"
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (
            request.user
            and request.user.is_authenticated
            and request.user.type == "business"
        )

class isOfferCreator(permissions.BasePermission):
    """
    Custom permission to only allow the creator of an offer to delete it.
    """
    message = "Only the creator of this offer can delete it!"
    def has_object_permission(self, request, view, obj):
        if request.method == "DELETE":
            return obj.user == request.user
        return True