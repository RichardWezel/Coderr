from decimal import Decimal
from django.db import transaction
from collections import OrderedDict
from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail
from auth_app.models import CustomUser

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
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError("Price must be a number.")
        if Decimal(value) < 0:
            raise serializers.ValidationError("Price must be a non-negative number.")
        return Decimal(value)
    
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
        request = self.context.get('request')
        has_pk = request and request.parser_context and request.parser_context.get('kwargs', {}).get('pk')

        items = []
        for d in instance.details.all().only('id'):
            rel_url = reverse('offers:offerdetail-detail', args=[d.id], request=request if has_pk else None)

            if has_pk:
                # Absolute URL mit Domain
                url = rel_url  # z.B. "http://127.0.0.1:8000/api/offerdetails/199/"
            else:
                # Relative kurze URL
                path = urlparse(rel_url).path.lstrip('/')
                if path.startswith('api/'):
                    path = path[3:]  # "offerdetails/2/"
                url = path

            items.append({"id": d.id, "url": url})
        return items


    def _full_details(self, instance):
        return OfferDetailSerializer(instance.details.all(), many=True, context=self.context).data
    
    def validate(self, attrs):
        request = self.context.get('request')
        method = getattr(request, 'method', 'GET').upper() if request else 'GET'
        details = self.initial_data.get('details', None)

        allowed = {c[0] for c in OfferDetail.Roles.choices}

        if method == 'POST':
            if not isinstance(details, list) or len(details) != 3:
                raise serializers.ValidationError({'details': 'Exactly 3 details (basic, standard, premium) are required.'})
            types = [d.get('offer_type') for d in details]
            if set(types) != allowed:
                raise serializers.ValidationError({'details': f'Must include exactly one of each: {sorted(allowed)}.'})

        if method in ('PUT', 'PATCH') and details is not None:
            if not isinstance(details, list) or len(details) == 0:
                raise serializers.ValidationError({'details': 'If provided, details must be a non-empty list.'})
            for d in details:
                ot = d.get('offer_type')
                if ot not in allowed:
                    raise serializers.ValidationError({'details': f'Each detail must include a valid offer_type in {sorted(allowed)}.'})

        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get('request')
        method = getattr(request, 'method', 'GET').upper() if request else 'GET'
        details_value = (
            self._full_details(instance) if method == 'POST' or (method in ('PUT', 'PATCH') and 'details' in self.initial_data)
            else self._thin_details(instance)
        )
        ordered_fields = ['id', 'user', 'title', 'image', 'description','created_at', 'updated_at','details','min_price', 'min_delivery_time','user_details',]

        new = OrderedDict()
        for f in ordered_fields:
            if f == 'details':
                new['details'] = details_value
            else:
                new[f] = rep.get(f)
        return new
    
    def _recalc_min_fields(self, offer: Offer):
        qs = offer.details.all()
        if not qs.exists():
            offer.min_price = None
            offer.min_delivery_time = None
        else:
            offer.min_price = min(d.price for d in qs)
            offer.min_delivery_time = min(d.delivery_time_in_days for d in qs)
        offer.save(update_fields=['min_price', 'min_delivery_time'])
  

    @transaction.atomic
    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        user = self.context['request'].user

        offer = Offer.objects.create(user=user, **validated_data)

        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)

        self._recalc_min_fields(offer)
        return offer
    
    @transaction.atomic
    def update(self, instance: Offer, validated_data):
        """
        PATCH/PUT: Falls 'details' übergeben werden, MUSS jedes Element 'offer_type' enthalten.
        Wir suchen das vorhandene Detail zu diesem Typ und aktualisieren nur die übergebenen Felder.
        """
        details_data = validated_data.pop('details', None)

        # Zuerst das Offer selbst (title, description, image, ...)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            # Map für schnelleren Zugriff
            existing_by_type = {d.offer_type: d for d in instance.details.all()}

            allowed = {c[0] for c in OfferDetail.Roles.choices}
            for payload in details_data:
                ot = payload.get('offer_type')
                if ot not in allowed:
                    raise serializers.ValidationError({'details': f'Invalid offer_type: {ot}'})
                if ot not in existing_by_type:
                    # Optional: Streng sein und Fehler werfen, falls ein Typ fehlt:
                    raise serializers.ValidationError({'details': f'Offer does not have a detail for type "{ot}". You must maintain exactly one per type.'})

                detail = existing_by_type[ot]

                # Nur Felder updaten, die im Payload enthalten sind:
                updatable_fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features']
                for f in updatable_fields:
                    if f in payload:
                        setattr(detail, f, payload[f])
                detail.save()

        # min_* neu berechnen
        self._recalc_min_fields(instance)
        return instance
    
# class OfferDetaisPKSerializer(serializers.ModelSerializer):
    
#     class Meta:
#         model = OfferDetail
#         fields = ['id', 'title', 'revisions','image','description', 'created_at', 'updated_at', 'details', 'min_price']

    