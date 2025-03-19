import logging
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .serializer import (
    MyTokenObtainPairSerializer,
    RegisterSerializer,
    UserSerializer,
    SignInWithGoogleSerializer,
    SendEmailVerificationSerializer,
    VerifyEmailSerializer
)
from .models import MyUser

logger = logging.getLogger(__name__)

class SendEmailVerificationView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SendEmailVerificationSerializer

    def post(self, request):
        user = request.user
        if user.is_authenticated and not user.is_verified:
            try:
                # Generate JWT token for email verification
                token = AccessToken.for_user(user)
                token['email_verification'] = True  # Custom claim
                token.set_exp(lifetime=timedelta(minutes=20))  # Token expires in 20 minutes

                # Generate verification link
                verification_link = f"http://localhost:5173/email-verify/?token={str(token)}"

                # Send the verification email
                send_mail(
                    subject="Verify Your Email",
                    message=f"Click the link to verify your email: {verification_link}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                )

                return Response(
                    {"success": "Verification email sent successfully."},
                    status=status.HTTP_200_OK
                )
            except Exception as e:
                logger.error("Error sending email verification: %s", str(e), exc_info=True)
                return Response(
                    {"error": "Internal server error. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            {"error": "User is already verified or not authenticated."},
            status=status.HTTP_400_BAD_REQUEST
        )


class VerifyEmailView(APIView):
    serializer_class = VerifyEmailSerializer

    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Decode the JWT token
            decoded_token = AccessToken(token)

            # Check that the token is intended for email verification
            if decoded_token.get('email_verification'):
                user_id = decoded_token.get('user_id')
                if not user_id:
                    logger.warning("Token payload missing user_id.")
                    return Response(
                        {"error": "Invalid token payload."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    user = MyUser.objects.get(pk=user_id)
                except MyUser.DoesNotExist:
                    logger.warning("User with id %s does not exist.", user_id)
                    return Response(
                        {"error": "User does not exist."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                # Mark user as verified
                user.is_verified = True
                user.save()
                return Response(
                    {"success": "Email verified successfully."},
                    status=status.HTTP_200_OK
                )
            else:
                logger.warning("Token does not have the email_verification claim.")
                return Response(
                    {"error": "Invalid verification token."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TokenError, InvalidToken) as e:
            logger.warning("Token error during email verification: %s", str(e))
            return Response(
                {"error": "Invalid or expired verification link."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Unexpected error during email verification: %s", str(e), exc_info=True)
            return Response(
                {"error": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RegisterUserView(APIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        signin_method = request.data.get('signin_method', 'email_password')  # Default method
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = MyUser.objects.create_user(
                    email=serializer.validated_data['email'],
                    password=request.data.get('password'),  # Ensure password is provided
                    first_name=serializer.validated_data.get('first_name', ''),
                    last_name=serializer.validated_data.get('last_name', ''),
                    signin_method=signin_method
                )
                user.save()
                return Response(
                    UserSerializer(user).data,
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                logger.error("Error during user registration: %s", str(e), exc_info=True)
                return Response(
                    {"error": "Internal server error. Please try again later."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            logger.info("User registration validation failed: %s", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class GoogleSignInView(GenericAPIView):
    serializer_class = SignInWithGoogleSerializer

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response(
                {"error": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            # Verify the Google token
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), settings.GOOGLE_CLIENT_ID)
            email = idinfo.get('email')
            first_name = idinfo.get('given_name', '')
            last_name = idinfo.get('family_name', '')

            if not email:
                logger.warning("Email not found in Google token.")
                return Response(
                    {"error": "Email not found in token."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Retrieve or create the user
            user, created = MyUser.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": first_name,
                    "last_name": last_name,
                    "signin_method": "google",
                    "is_verified": True
                }
            )
            if created:
                user.set_unusable_password()  # Disable password for Google sign-ins
                user.save()

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            user_data = UserSerializer(user).data
            return Response(
                {
                    "user": user_data,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
                status=status.HTTP_200_OK
            )

        except ValueError as ve:
            logger.warning("Invalid Google token: %s", str(ve))
            return Response(
                {"error": "Invalid token."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error("Error during Google sign-in: %s", str(e), exc_info=True)
            return Response(
                {"error": "Internal server error. Please try again later."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
