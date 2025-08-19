from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from auth_app.models import CustomUser
from reviews_app.models import Review

class OfferSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, queryset=CustomUser.objects.all())
    details = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [id, 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details')
    
    
class OfferDetailSerializer(serializers.ModelSerializer):
    revisions = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ('id', 'revisions')

    def get_revisions(self, obj):
        
        return Review.objects.filter(business_user_id=obj.business_user_id).count()