from rest_framework.permissions import BasePermission
from reviews_app.models import Review

class OneReviewPerBusinessUserPermission(BasePermission):
    """Limit each reviewer to a single review per business user (on POST)."""
    message = "You have already reviewed this business user."
    def has_permission(self, request, view):
        if request.method != 'POST':
            return True

        business_user_id = request.data.get('business_user')
        if not business_user_id or not request.user.is_authenticated:
            return False

        return not Review.objects.filter(
            reviewer=request.user,
            business_user_id=business_user_id
        ).exists()

class IsReviewerOrReadOnly(BasePermission):
    """Allow read to all; write only to the review's author."""
    message = "You do not have permission to modify this review."

    def has_object_permission(self, request, view, obj):
        """Grant safe methods; require ownership for mutations."""
        # Lesezugriff für alle erlaubt
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Schreibzugriff nur für den Ersteller der Review
        return obj.reviewer == request.user
    
class IsCustomerUser(BasePermission):
    """Ensure only non-business (customer) users can create reviews."""
    message = "Only customer users can create reviews."

    def has_permission(self, request, view):
        """Allow non-POST; for POST ensure requester is not a business user."""
        if request.method != 'POST':
            return True
        return request.user.is_authenticated and not request.user.type == 'business'
