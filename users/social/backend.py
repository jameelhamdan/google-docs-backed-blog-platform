from django.conf import settings
from django.urls import reverse
from django.forms import ValidationError
from oauthlib.oauth2 import WebApplicationClient
import requests
import json
from django.contrib.auth import get_user_model

AUTH_MODEL = get_user_model()


class GoogleOAuthClient:
    name = settings.SOCIAL_BACKEND_NAME
    AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth'
    ACCESS_TOKEN_URL = 'https://oauth2.googleapis.com/token'
    REVOKE_TOKEN_URL = 'https://oauth2.googleapis.com/revoke'
    USER_INFO_URL = 'https://openidconnect.googleapis.com/v1/userinfo'
    DEFAULT_SCOPE = ['openid', 'email', 'profile', 'https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']
    GOOGLE_DISCOVERY_URL = (
        'https://accounts.google.com/.well-known/openid-configuration'
    )

    GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
    GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET

    complete_url_name = 'users:social_complete'

    def __init__(self):
        self.client = WebApplicationClient(self.GOOGLE_CLIENT_ID)

    def get_request_uri(self, request):
        """
        Return url for authentication by provider
        :param request: django request
        :return: str, prepared uri
        """
        # Use library to construct the request for login and provide
        # scopes that let you retrieve user's profile from Google
        redirect_uri = request.build_absolute_uri(reverse(self.complete_url_name))
        return self.client.prepare_request_uri(
            self.AUTHORIZATION_URL,
            redirect_uri=redirect_uri,
            scope=self.DEFAULT_SCOPE,
        )

    def get_info_after_complete(self, request):
        """
        Parse request after being redirect back from google and returning user info
        :param request: http request
        :return: dict
        """
        # Get authorization code Google sent back
        code = request.GET.get('code')
        # Find out what URL to hit to get tokens that allow you to ask for
        # Prepare and send request to get tokens! Yay tokens!
        token_url, headers, body = self.client.prepare_token_request(
            self.ACCESS_TOKEN_URL,
            authorization_response=request.build_absolute_uri(request.path),
            redirect_url=request.build_absolute_uri(request.path),
            code=code,
        )

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
        response_json = user_info_response.json()

        if not response_json.get('email_verified'):
            raise ValidationError('Email not verified')

        final_info = dict()
        field_mapping = AUTH_MODEL.FIELD_MAPPING[self.name]
        for name, value in response_json.items():
            # Convert to existing user field if mapping exists
            name = field_mapping.get(name, name)
            if value is None or not hasattr(response_json, name):
                continue

            current_value = getattr(response_json, name, None)
            if current_value == value:
                continue

            setattr(final_info, name, value)

        return final_info

    def get_user(self, email):
        try:
            user = AUTH_MODEL.objects.get(email=email)
            return user
        except AUTH_MODEL.DoesnotExist:
            return None

    def create_or_update_user(self, user_info):
        user = self.get_user(user_info['email'])

        if user:
            # Update user
            protected = AUTH_MODEL.PROTECTED_FIELDS
            field_mapping = AUTH_MODEL.FIELD_MAPPING[self.name]
            for name, value in user_info.items():
                # Convert to existing user field if mapping exists
                name = field_mapping.get(name, name)
                if value is None or not hasattr(user_info, name) or name in protected:
                    continue

                current_value = getattr(user.data, name, None)
                if current_value == value:
                    continue

                setattr(user.data, name, value)

            user.data.save()

        else:
            # Create User
            user = get_user_model().create_user(user_info['username'].lower(), user_info['email'], None, **user_info)

        return user
