from rest_framework import serializers
from profile_app.models import UserProfile
from profile_app.models import FileUpload


class UserProfileSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'username', 'type', 'created_at']

    def _validate_name(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Must be a string.")
        value = value.strip()
        if any(ch.isdigit() for ch in value):
            raise serializers.ValidationError("No digits allowed in name.")
        if not all(ch.isalpha() or ch in " -'" for ch in value):
            raise serializers.ValidationError("Invalid characters in name.")
        return value

    def validate_tel(self, value):
        if value and not str(value).isdigit() and len(str(value)) > 0 and not str(value):
            raise serializers.ValidationError("Phone number must contain only digits in a string.")
        return value

    def validate_username(self, value):
        qs = UserProfile.objects.filter(username=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate_first_name(self, value):
        return self._validate_name(value)

    def validate_last_name(self, value):
        return self._validate_name(value)

    def validate_location(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Location must be a string.")
        return value.strip()

    def validate_working_hours(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Working hours must be a string.")
        return value.strip()

    def validate_description(self, value):
        if not isinstance(value, str):
            raise serializers.ValidationError("Description must be a string.")
        value = value.strip()
        if value.isdigit():
            raise serializers.ValidationError("Description cannot be only digits.")
        return value

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUpload
        fields = ['file', 'uploaded_at']

    
        