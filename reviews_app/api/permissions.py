from rest_framework.permissions import BasePermission
from reviews_app.models import Review

class OneReviewPerBusinessUserPermission(BasePermission):
    """
    Erlaubt das Posten einer Review nur, wenn der request.user
    noch keine Review für den angegebenen business_user erstellt hat.
    """
    message = "You have already reviewed this business user."
    def has_permission(self, request, view):
        # Nur für POST-Anfragen prüfen
        if request.method != 'POST':
            return True

        business_user_id = request.data.get('business_user')
        if not business_user_id or not request.user.is_authenticated:
            return False

        # Prüfen, ob bereits eine Review existiert
        return not Review.objects.filter(
            reviewer=request.user,
            business_user_id=business_user_id
        ).exists()