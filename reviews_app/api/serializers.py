from rest_framework import serializers
from reviews_app.models import Review

from auth_app.models import CustomUser


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating and listing reviews.

    Enforces BUSINESS role for `business_user` and prevents self-reviews.
    """
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type=CustomUser.Roles.BUSINESS),
        error_messages={
            "does_not_exist": "business_user with the given id does not exist.",
            "incorrect_type": "business_user must be a valid integer.",
        },
    )
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id', 
            'business_user', 
            'reviewer', 
            'rating', 
            'description',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'reviewer', 'updated_at']
        write_only_fields = ['business_user', 'rating', 'description']

    def validate_business_user(self, value: int):
        """Ensure the target is a BUSINESS user and not the requester."""
        if getattr(value, "type", None) != CustomUser.Roles.BUSINESS:
            raise serializers.ValidationError("The business_user must have the role BUSINESS.")
        if self.context.get("request") and self.context["request"].user == value:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def create(self, validated_data):
        """Attach the authenticated user as reviewer and create the review."""
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)
    
class ReviewDetailSerializer(serializers.ModelSerializer):
    """Serializer for retrieving/updating a single review instance."""
    business_user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(type=CustomUser.Roles.BUSINESS),
        error_messages={
            "does_not_exist": "business_user with the given id does not exist.",
            "incorrect_type": "business_user must be a valid integer.",
        },
    )
    rating = serializers.IntegerField(min_value=1, max_value=5)

    class Meta:
        model = Review
        fields = [
            'id', 
            'business_user', 
            'reviewer', 
            'rating', 
            'description',
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'reviewer', 'updated_at', 'business_user']
        write_only_fields = ['rating', 'description']

    def validate_business_user(self, value: int):
        """Ensure business_user remains a BUSINESS role (read-only here)."""
        if getattr(value, "type", None) != CustomUser.Roles.BUSINESS:
            raise serializers.ValidationError("The business_user must have the role BUSINESS.")
        if self.context.get("request") and self.context["request"].user == value:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def update(self, instance, validated_data):
        """Permit updates only by the review's author (reviewer)."""
        request = self.context.get("request")
        if request and request.user != instance.reviewer:
            raise serializers.ValidationError("You do not have permission to edit this review.")
        return super().update(instance, validated_data)
