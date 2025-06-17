from rest_framework import serializers
from django.contrib.auth.models import User
from auth_app.models import CustomUser

class RegistrationSerializer(serializers.ModelSerializer):

    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, data):
        if data['password'] != data['repeated_password']:
            raise serializers.ValidationError("Passwörter stimmen nicht überein.")
        if CustomUser.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Diese E-Mail wird bereits verwendet.")
        return data

    def create(self, validated_data):
        validated_data.pop('repeated_password')
        user = CustomUser(
            email=validated_data['email'],
            fullname=validated_data['fullname']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


