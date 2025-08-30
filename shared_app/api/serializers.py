from rest_framework import serializers
from reviews_app.models import Review
from auth_app.models import CustomUser
from offers_app.models import Offer
from django.db import models

class BaseInfoSerializer(serializers.Serializer):
    review_count = serializers.IntegerField(read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    business_profile_count = serializers.IntegerField(read_only=True)
    offer_count = serializers.IntegerField(read_only=True)

    class Meta:
        fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']
        read_only_fields = ['review_count', 'average_rating', 'business_profile_count', 'offer_count']



