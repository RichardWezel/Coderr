from rest_framework import serializers
from profile_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'email', 'username', 'type', 'created_at']

    def validate_user(self, attrs):
        if 'user' in self.initial_data:
            raise serializers.ValidationError(
                {'user': 'User field cannot be set directly.'}
            )
        return attrs
    
    def validate_username(self, value):
        if UserProfile.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                {'username': 'This username is already taken.'}
            )
        return value
    
    def validate_tel(self, attrs):
        if 'tel' in self.initial_data and not attrs['tel'].isdigit():
            raise serializers.ValidationError(
                {'tel': 'Phone number must contain only digits.'}
            )
        return super().validate(attrs)
    
    def validate_string(self, attrs):
        if 'location' in self.initial_data and not isinstance(attrs['location'], str):
            raise serializers.ValidationError(
                {'location': 'Location must be a string.'}
            )
        if 'first_name' in self.initial_data and not isinstance(attrs['first_name'], str):
            raise serializers.ValidationError(
                {'first_name': 'First Name must be a string.'}
            )
        if 'last_name' in self.initial_data and not isinstance(attrs['last_name'], str):
            raise serializers.ValidationError(
                {'last_name': 'Last Name must be a string.'}
            )
        if 'description' in self.initial_data and not isinstance(attrs['description'], str):
            raise serializers.ValidationError(
                {'description': 'Description must be a string.'}
            )
        if 'working-hours' in self.initial_data and not isinstance(attrs['working-hours'], str):
            raise serializers.ValidationError(
                {'working-hours': 'Working-Hours must be a string.'}
            )
        return super().validate(attrs)
    



    
        