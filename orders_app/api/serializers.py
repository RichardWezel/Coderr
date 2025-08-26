from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail
from auth_app.models import CustomUser

class OrderSerializer(serializers.ModelSerializer):

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
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError("OfferDetail with this id does not exist.")
        return value
    
    def validate(self, attrs):
        request = self.context.get('request')
        user: CustomUser = getattr(request, 'user', None)

        if not user or not user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Der Kunde muss vom Typ CUSTOMER sein
        if getattr(user, 'type', None) != CustomUser.Roles.CUSTOMER:
            raise serializers.ValidationError("Only customers can create orders.")

        # OfferDetail prüfen und Anbieter ermitteln
        od = OfferDetail.objects.select_related('offer', 'offer__user').get(id=attrs['offer_detail_id'])
        business_user = od.offer.user

        # Optional: Nutzer darf nicht sein eigenes Angebot bestellen
        if business_user_id := getattr(business_user, 'id', None):
            if user.id == business_user_id:
                raise serializers.ValidationError("You cannot order your own offer.")

        return attrs
    
    def create(self, validated_data):
        request = self.context['request']
        customer_user: CustomUser = request.user

        # OfferDetail + Offer holen
        od = OfferDetail.objects.select_related('offer', 'offer__user').get(id=validated_data['offer_detail_id'])
        related_offer = od.offer
        business_user = related_offer.user

        # Order-Snapshot auf Basis des OfferDetails
        order = Order.objects.create(
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
        return order