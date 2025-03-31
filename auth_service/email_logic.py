import base64
import smtplib
from email.mime.text import MIMEText
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from datetime import datetime
from auth_service.models import GoogleOAuthToken, MyUser
import os

def generate_xoauth2_string(username, access_token):
    auth_string = f"user={username}\x01auth=Bearer {access_token}\x01\x01"
    return base64.b64encode(auth_string.encode('utf-8')).decode('utf-8')

def refresh_google_token(user):
    """Refresh the Google OAuth2 access token if expired and update the database."""
    try:
        token_entry = user.google_oauth_token  # Access related token entry
    except GoogleOAuthToken.DoesNotExist:
        raise Exception("No Google OAuth token found for this user.")

    credentials = Credentials(
        token=token_entry.access_token,
        refresh_token=token_entry.refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )

    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())

        # Update the token in the database
        token_entry.update_tokens(credentials.token, credentials.refresh_token, credentials.expiry)

    return token_entry.access_token

def store_google_oauth_token(user, access_token, refresh_token, expires_in):
    """Store the OAuth2 token in the database when a user logs in."""
    token_entry, created = GoogleOAuthToken.objects.get_or_create(user=user)
    token_entry.update_tokens(access_token, refresh_token, expires_in)

def send_email_via_gmail_oauth2(user, recipient_email, subject, body):
    """Send an email using Gmail API with OAuth2 authentication."""
    access_token = refresh_google_token(user)  # Ensure we have a valid token
    xoauth2_string = generate_xoauth2_string(user.email, access_token)

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = user.email
    msg['To'] = recipient_email

    smtp_conn = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_conn.ehlo()
    smtp_conn.starttls()
    smtp_conn.ehlo()

    auth_command = 'AUTH XOAUTH2 ' + xoauth2_string
    code, response = smtp_conn.docmd(auth_command)
    if code != 235:
        smtp_conn.quit()
        raise Exception(f"Authentication error: {code} {response}")
    
    smtp_conn.sendmail(user.email, [recipient_email], msg.as_string())
    smtp_conn.quit()


class GmailOAuth2EmailBackend(BaseEmailBackend):
    """
    A Django email backend that sends email via Gmail using OAuth2,
    automatically refreshing the access token when needed.
    """
    
    def send_messages(self, email_messages):
        num_sent = 0
        sender_email = settings.GMAIL_SENDER_EMAIL

        for message in email_messages:
            try:
                recipient_email = message.to[0]
                user = MyUser.objects.get(email=sender_email)  # Fetch user by email
                send_email_via_gmail_oauth2(
                    user=user,
                    recipient_email=recipient_email,
                    subject=message.subject,
                    body=message.body,
                )
                num_sent += 1
            except Exception as e:
                if not self.fail_silently:
                    raise e
        return num_sent
