from rest_framework import serializers
from django.contrib.auth.models import User

from auth_app.models import CustomUser


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.

    This serializer handles user registration by requiring a full name,
    email, password, and a repeated password for confirmation.
    The password is write-only and will not appear in any API responses.
    """
    
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        """
        Validate user input during registration.

        Ensures that the provided passwords match and that the email
        address has not already been registered.

        Raises:
            serializers.ValidationError: If the passwords do not match
            or if the email is already in use.
        """

        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return data

    def create(self, validated_data):
        """
        Create a new user instance with hashed password.

        Removes the repeated password from the validated data,
        hashes the password, and saves the user instance.

        Args:
            validated_data (dict): Validated user input data.

        Returns:
            CustomUser: The newly created user instance.
        """

        validated_data.pop('repeated_password')
        user = CustomUser(
            email=validated_data['email'],
            fullname=validated_data['fullname']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for returning user details.

    Provides read-only access to the user's ID and includes
    the email and full name in the response.
    """
    
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'fullname']
        read_only_fields = ['id']