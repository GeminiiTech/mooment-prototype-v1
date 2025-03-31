import os
from google_auth_oauthlib.flow import InstalledAppFlow

# Build your client configuration dictionary using environment variables
client_config = {
    "installed": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        # "project_id": "your_project_id",  # You can set this if you have a value; it's optional here.
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret":os.getenv("GOOGLE_CLIENT_SECRET"),
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
