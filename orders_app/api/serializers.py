from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail
from auth_app.models import CustomUser
from rest_framework.exceptions import NotFound

class OrderCreateSerializer(serializers.ModelSerializer):
    """Create serializer for Orders using an OfferDetail as source.

    Takes `offer_detail_id` as input and derives immutable fields from the
    referenced OfferDetail and its parent Offer.
    """

    offer_detail_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 
            'offer_detail_id', 
            'customer_user', 
            'business_user', 
            'title', 
            'revisions', 
            'delivery_time_in_days', 
            'price', 
            'features',
            'offer_type', 
            'status', 
            'created_at', 
            'updated_at']
        read_only_fields = (
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        )
    
    def validate_offer_detail_id(self, value: int):
        """Ensure a positive integer and that the OfferDetail exists."""
        if value <= 0:
            raise serializers.ValidationError("offer_detail_id must be a positive integer.")
        try:
            OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise NotFound("OfferDetail with this id does not exist.")
        return value
    
    def validate_user_type(self, user: CustomUser):
        """Validate that the requesting user has CUSTOMER role."""
        if not user or not user.is_authenticated or getattr(user, "type", None) != CustomUser.Roles.CUSTOMER:
            raise serializers.ValidationError("Only users with role CUSTOMER can create orders.")
        return user
    
    def create(self, validated_data):
        """Create an Order from the selected OfferDetail and current user."""
        request = self.context['request']
        customer_user: CustomUser = request.user

        od = OfferDetail.objects.select_related('offer', 'offer__user').get(id=validated_data['offer_detail_id'])
        related_offer = od.offer
        business_user = related_offer.user

        return Order.objects.create(
            offer=related_offer,
            offer_detail=od,
            customer_user=customer_user,
            business_user=business_user,
            title=od.title,
            revisions=od.revisions,
            delivery_time_in_days=od.delivery_time_in_days,
            price=od.price,
            features=od.features,
            offer_type=od.offer_type,
            status=Order.OrderStatus.IN_PROGRESS,  
        )
    
class OrderReadSerializer(serializers.ModelSerializer):
    """Read-only serializer for returning Orders to clients."""
    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields  

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """Serializer to update Order status with valid transitions only."""
    class Meta:
        model = Order
        fields = ['status']  

    def validate_status(self, value):
        """Enforce allowed status transitions from IN_PROGRESS to final states."""
        instance: Order = self.instance
        if not instance:
            return value

        allowed_from = [Order.OrderStatus.IN_PROGRESS]
        allowed_to = [Order.OrderStatus.COMPLETED, Order.OrderStatus.CANCELLED]

        if instance.status not in allowed_from:
            raise serializers.ValidationError("Only orders with status 'in_progress' can be updated.")

        if value not in allowed_to:
            raise serializers.ValidationError(f"Status can only transition to {allowed_to}.")

        return value
    
class OrderCountSerializer(serializers.ModelSerializer):
    """Serializer for count responses on orders (read-only)."""
    class Meta:
        model = Order
        fields = ['order_count']  
        read_only_fields = fields
