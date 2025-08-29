from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail
from auth_app.models import CustomUser
from rest_framework.exceptions import NotFound

class OrderCreateSerializer(serializers.ModelSerializer):

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
        if value <= 0:
            raise serializers.ValidationError("offer_detail_id must be a positive integer.")
        try:
            OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise NotFound("OfferDetail with this id does not exist.")
        return value
    
    def validate_user_type(self, user: CustomUser):
        if not user or not user.is_authenticated or getattr(user, "type", None) != CustomUser.Roles.CUSTOMER:
            raise serializers.ValidationError("Only users with role CUSTOMER can create orders.")
        return user
    
    def create(self, validated_data):
        request = self.context['request']
        customer_user: CustomUser = request.user

        # OfferDetail + Offer holen
        od = OfferDetail.objects.select_related('offer', 'offer__user').get(id=validated_data['offer_detail_id'])
        related_offer = od.offer
        business_user = related_offer.user

        # Order-Snapshot auf Basis des OfferDetails
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
            status=Order.OrderStatus.IN_PROGRESS,  # default explizit
        )
    
class OrderReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            'id', 'customer_user', 'business_user', 'title', 'revisions',
            'delivery_time_in_days', 'price', 'features', 'offer_type',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = fields  # alles read-only

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']  # nur Status darf geupdatet werden

    def validate_status(self, value):
        # Optional: erlaubte Transitionen erzwingen
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