from rest_framework.permissions import BasePermission
from reviews_app.models import Review

class OneReviewPerBusinessUserPermission(BasePermission):
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
    message = "You do not have permission to modify this review."

    def has_object_permission(self, request, view, obj):
        # Lesezugriff für alle erlaubt
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        # Schreibzugriff nur für den Ersteller der Review
        return obj.reviewer == request.user