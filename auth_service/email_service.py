import resend
import os
from django.conf import settings

resend.api_key = settings.RESEND_API_KEY

def send_email(to_email, subject, html_content):
    return resend.Emails.send({
        "from": "moooments@resend.dev",
        "to": [to_email],
        "subject": subject,
        "html": html_content
    })
