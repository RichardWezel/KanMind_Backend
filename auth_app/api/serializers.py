from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration.
    It includes fields for the user's full name, email, password, and repeated
    password.
    The 'password' field is write-only to ensure it is not exposed in responses."""
    
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    #  Override the default validation to check for password match and existing email
    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return data

    #  Override the create method to handle password hashing
    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = CustomUser(
            email=validated_data['email'],
            fullname=validated_data['fullname']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details.
    It includes fields for the user's ID, email, and full name.
    The 'id' field is read-only to prevent modification."""
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']