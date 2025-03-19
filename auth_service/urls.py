from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import MyTokenObtainPairView, RegisterUserView, SendEmailVerificationView, VerifyEmailView,GoogleSignInView

urlpatterns = [

    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('signin-google/',GoogleSignInView.as_view(),name='signin_google'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('send-email-verification/', SendEmailVerificationView.as_view(), name='send_email_verification'),
    path('email-verify/', VerifyEmailView.as_view(), name='verify_email'),
]