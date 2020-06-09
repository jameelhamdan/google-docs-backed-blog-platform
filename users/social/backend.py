from django.conf import settings
from django.urls import reverse
from django.forms import ValidationError
from clients import google_client
from django.contrib.auth import get_user_model

AUTH_MODEL = get_user_model()


class GoogleOAuthClient:
    name = settings.SOCIAL_BACKEND_NAME
    complete_url_name = 'users:social_complete'
    AUTH_CLAIM = 'auth_info'

    def __init__(self):
        self.client = google_client.GoogleClient()

    def get_username(self, email):
        """
        Parses email to username
        :param email:
        :return: usernmae
        """

        return email.split('@')[0]

    def get_authorization_uri(self, request):
        """
        Return url for authentication by provider
        :param request: django request
        :return: str, prepared uri
        """
        redirect_uri = request.build_absolute_uri(reverse(self.complete_url_name))
        return self.client.get_authorization_uri(redirect_uri)

    def get_info_after_complete(self, request):
        """
        Parse request after being redirect back from google and returning user info
        :param request: http request
        :return: dict
        """
        # Get authorization code Google sent back
        code = request.GET.get('code')
        response_json, token_json = self.client.complete_authorization(code, request.build_absolute_uri(request.path))

        if not response_json.get('email_verified'):
            raise ValidationError('Email not verified')

        final_info = dict()
        field_mapping = AUTH_MODEL.FIELD_MAPPING[self.name]
        for name, value in response_json.items():
            # Convert to existing user field if mapping exists
            if value is None or not response_json.get(name):
                continue

            name_mapping = field_mapping.get(name, name)
            final_info[name_mapping] = value

        if not final_info.get('username'):
            final_info['username'] = self.get_username(final_info['email'])

        auth_into = token_json
        auth_into.update({'sub': response_json['sub']})
        final_info[self.AUTH_CLAIM] = {
            self.name: auth_into
        }

        return final_info

    def get_user(self, email):
        try:
            user = AUTH_MODEL.objects.get(email=email)
            return user
        except AUTH_MODEL.DoesNotExist:
            return None

    def create_or_update_user(self, user_info):
        user = self.get_user(user_info['email'])
        auth_info = user_info.pop(self.AUTH_CLAIM)

        if user:
            # Update user
            protected = AUTH_MODEL.PROTECTED_FIELDS
            field_mapping = AUTH_MODEL.FIELD_MAPPING[self.name]
            for name, value in user_info.items():
                # Convert to existing user field if mapping exists
                name = field_mapping.get(name, name)
                if value is None or not hasattr(user.data, name) or name in protected:
                    continue

                current_value = getattr(user.data, name, None)
                if current_value == value:
                    continue

                setattr(user.data, name, value)

            user.data.add_or_update_social_auth(auth_info)
            user.data.save()

        else:
            # Create User
            user = AUTH_MODEL.objects.create_user(user_info.pop('username').lower(), user_info.pop('email'), None, auth_info=auth_info, provider=self.name, **user_info)

        return user
