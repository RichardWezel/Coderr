from rest_framework import serializers
from profile_app.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):

    user = serializers.IntegerField(source='user.id', read_only=True)

    class Meta:
        model = UserProfile
        fields = ['user', 'username', 'first_name', 'last_name', 'file', 'location', 'tel', 'description', 'working_hours', 'type', 'email', 'created_at']
        read_only_fields = ['user', 'email', 'username', 'file', 'type', 'created_at']

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


    
        