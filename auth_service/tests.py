# import base64
# decoded_str = base64.b64decode('eyJzdGF0dXMiOiI0MDAiLCJzY2hlbWVzIjoiQmVhcmVyIiwic2NvcGUiOiJodHRwczovL21haWwuZ29vZ2xlLmNvbS8ifQ==').decode('utf-8')
# print(decoded_str)


import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Build your client configuration dictionary using environment variables
client_config = {
    "installed": {
        # "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "client_id": "210582870341-khspg9f95mqb5cp5j6o8rtcni9cgvvj4.apps.googleusercontent.com",
        "project_id": "your_project_id",  # You can set this if you have a value; it's optional here.
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}

# Define the required scopes (this one gives full access to Gmail)
scopes = ['https://mail.google.com/']

# Initialize the OAuth2 flow using the configuration dictionary
flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

# Run the flow: this will open a browser window for you to authorize your app
credentials = flow.run_local_server(port=8080)

# Print out the tokens
print("Access Token:", credentials.token)
print("Refresh Token:", credentials.refresh_token)
print(credentials.to_json())
