from oauthlib.oauth2 import WebApplicationClient
from django.conf import settings
import requests
import json


class GoogleClient(object):
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    REVOKE_TOKEN_URL = 'https://oauth2.googleapis.com/revoke'
    USER_INFO_URL = 'https://openidconnect.googleapis.com/v1/userinfo'
    ADD_DOCUMENT_URL = 'https://docs.googleapis.com/v1/documents'
    GET_DOCUMENT_URL = 'https://docs.googleapis.com/v1/documents/%(file_id)s'
    EXPORT_DOCUMENT_URL = 'https://docs.google.com/feeds/download/documents/export/Export?id=%(file_id)s&exportFormat=html'

    DEFAULT_SCOPE = [
        'openid', 'email', 'profile',
        'https://www.googleapis.com/auth/documents.readonly',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/documents',
        'https://www.googleapis.com/auth/drive.file'
    ]

    GOOGLE_DISCOVERY_URL = (
        'https://accounts.google.com/.well-known/openid-configuration'
    )

    GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

    def __init__(self):
        self.client = WebApplicationClient(self.GOOGLE_CLIENT_ID)

    def get_authorization_uri(self, redirect_uri):
        # Use library to construct the request for login and provide
        # scopes that let you retrieve user's profile from Google
        return self.client.prepare_request_uri(
            self.AUTHORIZATION_URL,
            redirect_uri=redirect_uri,
            scope=self.DEFAULT_SCOPE,
        )

    def complete_authorization(self, code, redirect_url):
        # Prepare token using oauth lib
        token_url, headers, body = self.client.prepare_token_request(
            self.ACCESS_TOKEN_URL,
            redirect_url=redirect_url,
            code=code,
            client_secret=self.GOOGLE_CLIENT_SECRET
        )

        # Check if tokens are valid by sending then to token endpoint
        token_response = requests.post(
            token_url,
            headers=headers,
            data=body,
            auth=(self.GOOGLE_CLIENT_ID, self.GOOGLE_CLIENT_SECRET),
        )

        # Parse the tokens!
        self.client.parse_request_body_response(json.dumps(token_response.json()))

        # Now that we have tokens (yay) let's find and hit URL
        # from Google that gives you user's profile information,
        # including their Google Profile Image and Email
        uri, headers, body = self.client.add_token(self.USER_INFO_URL)
        user_info_response = requests.get(uri, headers=headers, data=body)

        # We want to make sure their email is verified.
        # The user authenticated with Google, authorized our
        # app, and now we've verified their email through Google!
        return user_info_response.json(), token_response.json()
