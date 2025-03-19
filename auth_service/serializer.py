from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import MyUser

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = MyUser
        fields = ['id','password', 'email', 'first_name', 'last_name', 'signin_method', 'is_active','is_verified']
        read_only_fields = ['id', 'is_active']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = MyUser
        fields = ['email', 'password', 'first_name', 'last_name']

    def create(self, validated_data):
        return MyUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email
        token['is_verified'] = user.is_verified
        # ...

        return token
    
class SignInWithGoogleSerializer(serializers.Serializer):
    token = serializers.CharField()

class SendEmailVerificationSerializer(serializers.Serializer):
    """This serializer is now just a placeholder for structure but doesn't require any input."""
    pass

class VerifyEmailSerializer(serializers.Serializer):
    """This serializer is now just a placeholder for structure but doesn't require any input."""
    pass