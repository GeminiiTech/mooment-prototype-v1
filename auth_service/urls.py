from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, RegisterUserView, SendEmailVerificationView, VerifyEmailView,GoogleSignInView,SendPasswordResetLinkView,VerifyNewPasswordView

urlpatterns = [

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signin-google/',GoogleSignInView.as_view(),name='signin_google'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('send-email-verification/', SendEmailVerificationView.as_view(), name='send_email_verification'),
    path('email-verify/', VerifyEmailView.as_view(), name='verify_email'),
    path('send-password-reset-link/', SendPasswordResetLinkView.as_view(), name='password_reset'),
    path('verify-new-password/', VerifyNewPasswordView.as_view(), name='password_reset_confirm'),
]