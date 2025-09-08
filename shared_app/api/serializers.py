from rest_framework import serializers

class BaseInfoSerializer(serializers.Serializer):
    """Serializer for aggregate base info counts and averages.

    Returns counts for reviews, business profiles, offers and an average
    rating value limited to one decimal place.
    """
    review_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=1, read_only=True, allow_null=True)
    business_profile_count = serializers.IntegerField(read_only=True)
    offer_count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']
        read_only_fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']

