from django.db import transaction
from collections import OrderedDict
from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail
from auth_app.models import CustomUser
from reviews_app.models import Review

class OfferDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def validate_features(self, value):
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise serializers.ValidationError("features must be a list of strings.")
        return value
    
    def validate_title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Title must be a non-empty string.")
        return value.strip()
    
    def validate_revisions(self, value):
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Revisions must be a non-negative integer.")
        return value
    
    def validate_delivery_time_in_days(self, value):
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Delivery time must be a non-negative integer.")
        return value
    
    def validate_price(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise serializers.ValidationError("Price must be a non-negative number.")
        return value
    
    def validate_offer_type(self, value):
        if value not in [choice[0] for choice in OfferDetail.Roles.choices]:
            raise serializers.ValidationError(f"Offer type must be one of {OfferDetail.Roles.choices}.")
        return value

class OfferSerializer(serializers.ModelSerializer):

    details = OfferDetailSerializer(many=True, write_only=True, required=False)
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
        items = []
        for d in instance.details.all().only('id'):
            # relative URL (ohne Domain), z.B. "/api/offerdetails/2/"
            rel_url = reverse('offers:offerdetail-detail', args=[d.id])  # kein request!

            # auf "offerdetails/2/" normalisieren:
            path = urlparse(rel_url).path.lstrip('/')  # "api/offerdetails/2/"
            if path.startswith('api/'):
                path = path[4:]  # "offerdetails/2/"

            items.append({
                "id": d.id,
                "url": path,  # -> "offerdetails/2/"
            })
        return items

    def _full_details(self, instance):
        return OfferDetailSerializer(instance.details.all(), many=True, context=self.context).data
    
    def validate(self, attrs):
        request = self.context.get('request')
        if request and request.method.upper() == 'POST':
            details = self.initial_data.get('details', [])
            # lists haben kein .count() für Länge:
            if not isinstance(details, list) or len(details) < 3:
                raise serializers.ValidationError({'details': 'At least 3 details are required.'})
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
    
class OfferDetaisPKSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = OfferDetail
        fields = ['id', 'user', 'title', 'image','description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time']

    