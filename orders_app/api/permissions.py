# permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS
from auth_app.models import CustomUser
from orders_app.models import Order
from offers_app.models import OfferDetail

class IsCustomerForCreate(BasePermission):
    """
    Erlaubt POST nur für Nutzer mit Rolle CUSTOMER.
    GET (List) bleibt durch andere Permissions/IsAuthenticated abgedeckt.
    """

    message = "Only users with role CUSTOMER can create orders."
    
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "type", None) == CustomUser.Roles.CUSTOMER)

class NotOrderingOwnOffer(BasePermission):
    """
    Verbietet, das eigene Angebot zu bestellen (gilt nur für POST).
    Erwartet offer_detail_id im Request.
    """
    message = "You cannot order your own offer."

    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        od_id = request.data.get("offer_detail_id")
        if not od_id:
            return True  # Feldvalidierung übernimmt der Serializer
        try:
            od = OfferDetail.objects.select_related("offer", "offer__user").get(id=od_id)
        except OfferDetail.DoesNotExist:
            return True  # Serializer meldet „existiert nicht“
        return od.offer.user_id != request.user.id

class IsOrderParticipant(BasePermission):
    """
    Objektberechtigung: Nur Kunde oder Business der Order dürfen darauf zugreifen/ändern.
    """
    def has_object_permission(self, request, view, obj: Order):
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.customer_user_id == request.user.id or obj.business_user_id == request.user.id

class IsBusinessUser(BasePermission):
    """
    Erlaubt alle Methoden nur für Nutzer mit Rolle BUSINESS.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "type", None) == CustomUser.Roles.BUSINESS)