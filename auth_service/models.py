from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.timezone import now
from datetime import timedelta

# Create your CustomUserManager here
class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password must be provided")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

# Create your Custom User model here
class MyUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, max_length=255)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    SIGNIN_METHOD_CHOICES = [
        ('google', 'Google'),
        ('email_password', 'Email_Password'),
    ]
    signin_method = models.CharField(max_length=20, choices=SIGNIN_METHOD_CHOICES, default='email_password')


    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = 'MyUser'
        verbose_name_plural = 'MyUsers'


class GoogleOAuthToken(models.Model):
    """Stores OAuth tokens for Gmail API authentication."""
    user = models.OneToOneField(MyUser, on_delete=models.CASCADE, related_name="google_oauth_token")
    access_token = models.CharField(max_length=500)
    refresh_token = models.CharField(max_length=500)
    token_expiry = models.DateTimeField()

    def is_expired(self):
        """Check if the token is expired."""
        return self.token_expiry <= now()

    def update_tokens(self, access_token, refresh_token, expiry_seconds):
        """Update the access token, refresh token, and expiry time."""
        self.access_token = access_token
        if refresh_token:  # Only update if a new refresh token is provided
            self.refresh_token = refresh_token
        self.token_expiry = now() + timedelta(seconds=expiry_seconds)
        self.save()

    def __str__(self):
        return f"Google OAuth Token for {self.user.email}"