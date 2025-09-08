from rest_framework.permissions import BasePermission, SAFE_METHODS

from auth_app.models import CustomUser
from orders_app.models import Order
from offers_app.models import OfferDetail

class IsStaffOrAdminForDelete(BasePermission):
    """Allow DELETE only to staff or superusers; allow all other methods."""
    
    message = "Only staff users or admins can delete objects."

    def has_permission(self, request, view):
        """Grant permission for non-DELETE; enforce staff/admin for DELETE."""
        if request.method != "DELETE":
            return True
        user = request.user
        return bool(user and user.is_authenticated and (user.is_staff or user.is_superuser))

class IsCustomerForCreate(BasePermission):
    """Ensure only CUSTOMER users can create new orders."""

    message = "Only users with role CUSTOMER can create orders."

    def has_permission(self, request, view):
        """Allow SAFE methods; enforce CUSTOMER role otherwise."""
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "type", None) == CustomUser.Roles.CUSTOMER)

class NotOrderingOwnOffer(BasePermission):
    """Prevent users from ordering their own offers on POST requests."""
    
    message = "You cannot order your own offer."

    def has_permission(self, request, view):
        """Allow non-POST; for POST ensure selected OfferDetail isn't own."""
        if request.method != "POST":
            return True
        od_id = request.data.get("offer_detail_id")
        if not od_id:
            return True  
        try:
            od = OfferDetail.objects.select_related("offer", "offer__user").get(id=od_id)
        except OfferDetail.DoesNotExist:
            return True 
        return od.offer.user_id != request.user.id

class IsOrderParticipant(BasePermission):
    """Grant object access to order's customer or business user only."""
    
    def has_object_permission(self, request, view, obj: Order):
        """Check that the authenticated user participates in the order."""
        if not request.user or not request.user.is_authenticated:
            return False
        return obj.customer_user_id == request.user.id or obj.business_user_id == request.user.id

class IsBusinessUser(BasePermission):
    """Allow non-modifying methods; require BUSINESS role for writes."""
   
    def has_permission(self, request, view):
        """Allow SAFE methods; otherwise require BUSINESS role."""
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, "type", None) == CustomUser.Roles.BUSINESS)
