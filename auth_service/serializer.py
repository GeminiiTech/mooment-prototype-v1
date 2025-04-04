from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import MyUser
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.utils.encoding import force_str
# from .email_service import send_email


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

class SendPasswordResetLinkSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = MyUser.objects.get(email=value)
        except MyUser.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        reset_url = f"http://localhost:5173/reset-password/?uid={uid}&token={token}"

        send_mail(
            subject="Password Reset Request",
            message=f"Click the link to reset your password: /n {reset_url}",
            from_email="ettiolayinka4@gmail.com",
            recipient_list=[value],
            fail_silently=False,
        )
        # send_email(
        #     to_email=value,
        #     subject="Reset Password for your Moooments account",
        #     html_content=f"Click the link to reset your password: /n {reset_url}"
        # )
        return value
    
class VerifyNewPasswordSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            uid = force_str(urlsafe_base64_decode(data['uid']))
            user = MyUser.objects.get(pk=uid)
        except (MyUser.DoesNotExist, ValueError):
            raise serializers.ValidationError("Invalid user.")

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, data['token']):
            raise serializers.ValidationError("Invalid or expired token.")

        user.set_password(data['new_password'])
        user.save()
        return data