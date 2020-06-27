from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models, transaction
from django.urls import reverse_lazy
from django.conf import settings
from django.utils import timezone
from djongo.models.json import JSONField
from django import forms
import djongo.models as mongo
from _common import utils


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, auth_info=None, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not email:
            raise ValueError('The given email must be set')

        if not username:
            username = self.model.generate_username(email)

        provider = extra_fields.pop('provider')

        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            last_login=now,
            date_joined=now,
            name=extra_fields['name']
        )

        user.set_password(password)

        with transaction.atomic():
            user.save(using=self._db)
            user_data = UserData(
                pk=user.pk,
                username=user.username,
                email=user.email,
                **{k: v for k, v in extra_fields.items() if k in [k for k, v in self.model.FIELD_MAPPING[provider].items()]},
            )
            if auth_info:
                user_data.add_or_update_social_auth(auth_info)

            user_data.save()

        return user

    def create_user(self, username, email, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        return self._create_user(username, email, password, True, True, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=256, unique=True)
    username = models.EmailField(max_length=256, unique=True)
    name = models.CharField(max_length=256, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []
    PROTECTED_FIELDS = ['id', 'email', 'username', 'is_staff', 'is_superuser', 'is_active', 'last_login', 'date_joined']
    FIELD_MAPPING = {
        'default': {
            'email': 'email',
            'name': 'name',
            'given_name': 'given_name',
            'family_name': 'family_name',
            'avatar_url': 'avatar_url',
        },
        'google': {
            'email': 'email',
            'username': 'username',
            'picture': 'avatar_url',
            'name': 'name',
            'given_name': 'given_name',
            'family_name': 'family_name',
        }
    }

    _data = None

    def _query_data(self):
        return UserData.objects.get(pk=self.pk)

    def refresh_data(self):
        self._data = self._query_data()

    def _get_data(self):
        # TODO: improve this kind of instance cache (specially when changing UserData)
        if not self._data:
            self._data = self._query_data()
        return self._data

    @property
    def data(self):
        return self._get_data()

    def get_absolute_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.username})

    @staticmethod
    def generate_username(email):
        base_username = email.split('@')[0]
        return utils.klass_unique_slug_generator(User, base_username, slug_name='username', separator='')

    objects = UserManager()

    class Meta:
        db = settings.DEFAULT_DATABASE


class SocialAuth(mongo.Model):
    provider = mongo.CharField(max_length=32)
    uid = mongo.CharField(max_length=255)
    access_token = mongo.TextField(max_length=255)
    extra_data = JSONField(default={})
    created_on = mongo.DateTimeField()
    updated_on = mongo.DateTimeField()

    class Meta:
        abstract = True


class SocialAuthForm(forms.ModelForm):
    class Meta:
        model = SocialAuth
        fields = (
            'provider', 'uid', 'access_token', 'extra_data', 'updated_on', 'created_on'
        )


class UserData(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)
    email = mongo.EmailField(max_length=36, db_index=True, unique=True, null=False)
    username = mongo.CharField(max_length=256, db_index=True, unique=True, null=False)

    avatar_url = mongo.CharField(max_length=36)
    given_name = mongo.CharField(max_length=256, null=False)
    family_name = mongo.CharField(max_length=256, null=False)
    name = mongo.CharField(max_length=256, null=False)

    # Social Auth fields
    social_auth = mongo.ArrayField(
        model_container=SocialAuth,
        model_form_class=SocialAuthForm,
        default=[]
    )

    objects = mongo.DjongoManager()

    AUTH_FIELD_MAPPING = {
        'google': {
            'sub': 'uid',
            'access_token': 'access_token',
            'provider': 'provider',
        }
    }

    def get_absolute_url(self):
        return reverse_lazy('profile:profile', kwargs={'username': self.username})

    def get_access_token(self, provider='google'):
        for auth in self.social_auth:
            if auth['provider'] == provider:
                return auth['access_token']

        raise Exception('This provider is not active for this user!')

    def add_or_update_social_auth(self, new_data):
        for provider, data in new_data.items():
            now = timezone.now()
            new_social_auth = {
                'provider': provider,
                'access_token': data.pop('access_token'),
                'uid': data.pop('sub'),
                'extra_data': data,
                'updated_on': now
            }

            updated = False
            for index, social_auth in enumerate(self.social_auth):
                if social_auth['provider'] == provider:
                    new_social_auth['created_on'] = social_auth.get('created_on', now)
                    self.social_auth[index] = new_social_auth
                    updated = True
                    break

            if updated:
                continue

            new_social_auth['created_on'] = now
            # if Auth method doesn't exist add it
            self.social_auth += [new_social_auth]

    class Meta:
        db_table = 'user_data'
        db = settings.MONGO_DATABASE
