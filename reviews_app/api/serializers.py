from rest_framework import serializers
from reviews_app.models import Review
from auth_app.models import CustomUser
from rest_framework.exceptions import NotFound

class ReviewSerializer(serializers.ModelSerializer):
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
        if getattr(value, "type", None) != CustomUser.Roles.BUSINESS:
            raise serializers.ValidationError("The business_user must have the role BUSINESS.")
        if self.context.get("request") and self.context["request"].user == value:
            raise serializers.ValidationError("You cannot review yourself.")
        return value

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)