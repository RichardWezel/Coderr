from django.db import transaction
from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail
from auth_app.models import CustomUser
from reviews_app.models import Review

class OfferDetailFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def validate_features(self, value):
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise serializers.ValidationError("features muss eine Liste von Strings sein.")
        return value

class OfferDetailWriteSerializer(OfferDetailFullSerializer):
    pass

class OfferSerializer(serializers.ModelSerializer):

    details = OfferDetailWriteSerializer(many=True, write_only=True, required=False)
    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details')
    
    def get_user_details(self, obj):
        u: CustomUser = obj.user
        return {
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "username": u.username,
        }

    def _thin_details(self, instance):
        request = self.context.get('request')
        items = []
        for d in instance.details.all().only('id'):
            items.append({
                "id": d.id,
                "url": reverse('offers:offerdetail-detail', args=[d.id], request=request)
            })
        return items

    def _full_details(self, instance):
        return OfferDetailFullSerializer(instance.details.all(), many=True, context=self.context).data
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method.upper() == 'POST':
            details = self.initial_data.get('details', [])
            if not details:
                raise serializers.ValidationError({'details': 'Mindestens ein Paket (Detail) ist erforderlich.'})
        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)

        request = self.context.get('request')
        method = getattr(request, 'method', 'GET').upper() if request else 'GET'
        details_value = (
            self._full_details(instance) if method == 'POST'
            else self._thin_details(instance)
        )

        ordered_fields = [
            'id', 'user', 'title', 'image', 'description',
            'created_at', 'updated_at',
            'details',             
            'min_price', 'min_delivery_time',
            'user_details',
        ]

        new = OrderedDict()
        for f in ordered_fields:
            if f == 'details':
                new['details'] = details_value
            else:
                new[f] = rep.get(f)
        return new
  

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        user = self.context['request'].user

        offer = Offer.objects.create(user=user, **validated_data)

        min_price = None
        min_delivery = None

        for detail in details_data:
            d = OfferDetail.objects.create(offer=offer, **detail)
            if min_price is None or d.price < min_price:
                min_price = d.price
            if min_delivery is None or d.delivery_time_in_days < min_delivery:
                min_delivery = d.delivery_time_in_days

        offer.min_price = min_price
        offer.min_delivery_time = min_delivery
        offer.save(update_fields=['min_price', 'min_delivery_time'])

        return offer
    
class OfferDetailReviewsSerializer(serializers.ModelSerializer):
    reviews_count = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'delivery_time_in_days', 'price', 'features', 'offer_type', 'reviews_count']

    def get_reviews_count(self, obj):
        business_user = obj.offer.user
        return Review.objects.filter(business_user=business_user).count()