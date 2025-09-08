from rest_framework.permissions import BasePermission


class IsReviewerOrReadOnly(BasePermission):
    """Allow read to all; write only to the review's author."""
    message = "You do not have permission to modify this review."

    def has_object_permission(self, request, view, obj):
        """Grant safe methods; require ownership for mutations."""
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return obj.reviewer == request.user
    
class IsCustomerUser(BasePermission):
    """Ensure only non-business (customer) users can create reviews."""
    message = "Only customer users can create reviews."

    def has_permission(self, request, view):
        """Allow non-POST; for POST ensure requester is not a business user."""
        if request.method != 'POST':
            return True
        return request.user.is_authenticated and not request.user.type == 'business'
