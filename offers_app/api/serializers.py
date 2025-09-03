from decimal import Decimal
from django.db import transaction
from collections import OrderedDict
from urllib.parse import urlparse

from rest_framework import serializers
from rest_framework.reverse import reverse

from offers_app.models import Offer, OfferDetail
from auth_app.models import CustomUser

class OfferDetailSerializer(serializers.ModelSerializer):
    """Serializer for a single OfferDetail (pricing tier)."""
    class Meta:
        model = OfferDetail
        fields = ['id', 'title', 'revisions', 'delivery_time_in_days', 'price', 'features', 'offer_type']
        read_only_fields = ['id']

    def validate_features(self, value):
        """Ensure features is a list of strings."""
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise serializers.ValidationError("features must be a list of strings.")
        return value
    
    def validate_title(self, value):
        """Normalize and validate non-empty title."""
        if not isinstance(value, str) or not value.strip():
            raise serializers.ValidationError("Title must be a non-empty string.")
        return value.strip()
    
    def validate_revisions(self, value):
        """Ensure revisions is a non-negative integer."""
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Revisions must be a non-negative integer.")
        return value
    
    def validate_delivery_time_in_days(self, value):
        """Ensure delivery time is a non-negative integer (days)."""
        if not isinstance(value, int) or value < 0:
            raise serializers.ValidationError("Delivery time must be a non-negative integer.")
        return value
    
    def validate_price(self, value):
        """Ensure price is a non-negative Decimal."""
        if not isinstance(value, (int, float, Decimal)):
            raise serializers.ValidationError("Price must be a number.")
        if Decimal(value) < 0:
            raise serializers.ValidationError("Price must be a non-negative number.")
        return Decimal(value)
    
    def validate_features(self, value):
        """Ensure features is a list of strings."""
        if not isinstance(value, list):
            raise serializers.ValidationError("features must be a list of strings.")
        for v in value:
            if not isinstance(v, str):
                raise serializers.ValidationError("Each feature must be a string.")
        return value

    def validate_offer_type(self, value):
        """Validate offer_type against declared choices."""
        if value not in [choice[0] for choice in OfferDetail.OfferTypes.choices]:
            raise serializers.ValidationError(f"Offer type must be one of {OfferDetail.OfferTypes.choices}.")
        return value

    def to_representation(self, instance):
        """Optionally return parent Offer if explicitly requested via context.

        Avoids recursion during Offer updates by only triggering when a view
        sets context['return_parent_offer'] = True (e.g., OfferDetail update
        endpoints). Otherwise, returns the standard OfferDetail representation.
        """
        if self.context.get('return_parent_offer'):
            offer_serializer = OfferSerializer(
                instance.offer,
                context={**self.context, 'force_full_details': True}
            )
            return offer_serializer.data
        return super().to_representation(instance)

class OfferSerializer(serializers.ModelSerializer):
    """Serializer for Offer with nested OfferDetails handling and summaries."""

    details = OfferDetailSerializer(many=True, write_only=True, required=False)
    user_details = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Offer
        fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        read_only_fields = ('id', 'user', 'created_at', 'updated_at', 'min_price', 'min_delivery_time', 'user_details')
    
    def get_user_details(self, obj):
        """Expose lightweight user info for the offer owner."""
        u: CustomUser = obj.user
        return {
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "username": u.username,
        }

    def _thin_details(self, instance):
        """Return minimal detail objects with id and URL, optimized for list views."""
        request = self.context.get('request')
        has_pk = request and request.parser_context and request.parser_context.get('kwargs', {}).get('pk')

        items = []
        for d in instance.details.all().only('id'):
            url = self._detail_url_for_item(d.id, request, bool(has_pk))
            items.append({"id": d.id, "url": url})
        return items

    def _detail_url_for_item(self, detail_id, request, has_pk):
        """Build absolute URL when viewing a single offer, else relative path.

        Mirrors previous behavior: absolute URL with request for retrieve views,
        relative path without leading 'api/' for list views.
        """
        rel_url = reverse('offers:offerdetail-detail', args=[detail_id], request=request if has_pk else None)
        if has_pk:
            return rel_url
        path = urlparse(rel_url).path.lstrip('/')
        if path.startswith('api/'):
            path = path[3:]
        return path


    def _full_details(self, instance):
        """Return full nested details payload for create/update responses."""
        return OfferDetailSerializer(instance.details.all(), many=True, context=self.context).data
    
    def validate(self, attrs):
        """Route validation based on method and details payload size/contents."""
        request = self.context.get('request')
        method = getattr(request, 'method', 'GET').upper() if request else 'GET'
        details = self.initial_data.get('details', None)

        allowed = self._allowed_detail_types()

        if method == 'POST':
            self._validate_details_on_create(details, allowed)

        if method in ('PUT', 'PATCH') and details is not None:
            self._validate_details_on_update(details, allowed)

        return attrs

    def _allowed_detail_types(self):
        """Return the set of allowed OfferDetail types."""
        return {c[0] for c in OfferDetail.OfferTypes.choices}

    def _validate_details_on_create(self, details, allowed):
        """Validate that exactly one of each detail type is provided on create.

        Also validates that each detail contains a valid 'features' list[str].
        """
        if not isinstance(details, list) or len(details) != 3:
            raise serializers.ValidationError({'details': 'Exactly 3 details (basic, standard, premium) are required.'})
        types = [d.get('offer_type') for d in details]
        if set(types) != allowed:
            raise serializers.ValidationError({'details': f'Must include exactly one of each: {sorted(allowed)}.'})
        for d in details:
            self._assert_features_present_and_valid(d)

    def _validate_details_on_update(self, details, allowed):
        """Validate provided details list and types on update operations.

        If 'features' is provided, ensure it is list[str]; also catch 'feature' typo.
        """
        if not isinstance(details, list) or len(details) == 0:
            raise serializers.ValidationError({'details': 'If provided, details must be a non-empty list.'})
        for d in details:
            ot = d.get('offer_type')
            if ot not in allowed:
                raise serializers.ValidationError({'details': f'Each detail must include a valid offer_type in {sorted(allowed)}.'})
            if 'feature' in d and 'features' not in d:
                raise serializers.ValidationError({'details': "Unknown field 'feature'. Did you mean 'features' (list of strings)?"})
            if 'features' in d:
                self._assert_features_type(d['features'])

    def _assert_features_present_and_valid(self, payload):
        """Ensure payload contains 'features' and it is list[str]."""
        if 'feature' in payload and 'features' not in payload:
            raise serializers.ValidationError({'details': "Unknown field 'feature'. Use 'features' (list of strings)."})
        if 'features' not in payload:
            raise serializers.ValidationError({'details': "Each detail must include 'features' (list of strings)."})
        self._assert_features_type(payload['features'])

    def _assert_features_type(self, value):
        """Validate that 'features' is an array of strings and report bad positions."""
        if not isinstance(value, list):
            raise serializers.ValidationError({'details': "'features' must be an array (list) of strings."})
        bad_positions = [i for i, v in enumerate(value) if not isinstance(v, str)]
        if bad_positions:
            raise serializers.ValidationError({'details': f"All items in 'features' must be strings. Invalid at positions {bad_positions}."})

    def to_representation(self, instance):
        """Return ordered representation with either thin or full details.

        Full details are included after create/update when the request carries
        a details payload; otherwise a thin list of links is returned.
        """
        rep = super().to_representation(instance)
        method = self._request_method()
        details_value = self._compute_details_representation(instance, method)
        ordered_fields = ['id', 'user', 'title', 'image', 'description', 'created_at', 'updated_at', 'details', 'min_price', 'min_delivery_time', 'user_details']
        return self._ordered_representation(rep, details_value, ordered_fields)

    def _request_method(self):
        """Return uppercased request method or 'GET' if unavailable."""
        request = self.context.get('request')
        return getattr(request, 'method', 'GET').upper() if request else 'GET'

    def _compute_details_representation(self, instance, method):
        """Choose between full or thin details list based on context."""
        if self.context.get('force_full_details'):
            return self._full_details(instance)
        if method == 'POST' or (method in ('PUT', 'PATCH') and 'details' in getattr(self, 'initial_data', {})):
            return self._full_details(instance)
        return self._thin_details(instance)

    def _ordered_representation(self, rep, details_value, ordered_fields):
        """Rebuild OrderedDict in a stable field order, injecting details."""
        new = OrderedDict()
        for f in ordered_fields:
            if f == 'details':
                new['details'] = details_value
            else:
                new[f] = rep.get(f)
        return new
    
    def _recalc_min_fields(self, offer: Offer):
        """Recalculate and persist min_price and min_delivery_time."""
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
        """Create offer and its details atomically, then recalc min fields."""
        details_data = validated_data.pop('details', [])
        user = self.context['request'].user

        offer = Offer.objects.create(user=user, **validated_data)

        for detail in details_data:
            OfferDetail.objects.create(offer=offer, **detail)

        self._recalc_min_fields(offer)
        return offer
    
    @transaction.atomic
    def update(self, instance: Offer, validated_data):
        """Update offer fields, conditionally update details, then recalc mins."""
        details_data = validated_data.pop('details', None)
        instance = super().update(instance, validated_data)

        if details_data is not None:
            self._update_details(instance, details_data)

        self._recalc_min_fields(instance)
        return instance

    def _update_details(self, instance: Offer, details_data):
        """Apply partial updates to existing details matched by offer_type."""
        existing_by_type = {d.offer_type: d for d in instance.details.all()}
        allowed = self._allowed_detail_types()
        for payload in details_data:
            ot = payload.get('offer_type')
            if ot not in allowed:
                raise serializers.ValidationError({'details': f'Invalid offer_type: {ot}'})
            if ot not in existing_by_type:
                raise serializers.ValidationError({'details': f'Offer does not have a detail for type "{ot}". You must maintain exactly one per type.'})

            detail = existing_by_type[ot]
            updatable_fields = ['title', 'revisions', 'delivery_time_in_days', 'price', 'features']
            for f in updatable_fields:
                if f in payload:
                    setattr(detail, f, payload[f])
            detail.save()
