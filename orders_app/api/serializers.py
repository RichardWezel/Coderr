from rest_framework import serializers
from orders_app.models import Order
from auth_app.models import CustomUser

class OfferSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['id', 'offer_detail_id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at']
        read_only_fields = ('offer_detail_id')
    
    def validate_status(self, value):
        if value not in [choice[0] for choice in Order.OrderStatus.choices]:
            raise serializers.ValidationError(f"Status must be one of {Order.OrderStatus.choices}.")
        return value
    
    def validate_offer_detail_id(self, value):
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError("Offer Detail ID must be a positive integer.")
        return value
    
    def validate_customer_user(self, value):
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError("Customer User ID must be a positive integer.")
        if CustomUser.objects.filter(id=value).exists() is False:
            raise serializers.ValidationError("Customer User with this ID does not exist.")
        if CustomUser.objects.get(id=value).type != CustomUser.Roles.CUSTOMER:
            raise serializers.ValidationError("Customer User must be a customer.")
        return value
    
    def validate_business_user(self, value):
        if not isinstance(value, int) or value <= 0:
            raise serializers.ValidationError("Business User ID must be a positive integer.")
        if CustomUser.objects.filter(id=value).exists() is False:
            raise serializers.ValidationError("Business User with this ID does not exist.")
        if CustomUser.objects.get(id=value).type != CustomUser.Roles.BUSINESS:
            raise serializers.ValidationError("Business User must be a business.")
        return value