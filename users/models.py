from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
from django import forms
import djongo.models as mongo


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(
            username=username,
            email=email,
            is_staff=is_staff,
            is_active=True,
            last_login=now,
            date_joined=now,
            **extra_fields
        )

        user.set_password(password)

        user.save(using=self._db)

        UserData(
            pk=user.pk,
            username=user.username,
            email=user.email,
            **extra_fields
        ).save()

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
        'google': {
            'email': 'email',
            'username': 'username',
            'picture': 'avatar_url',
            'name': 'full_name',
            'given_name': 'given_name',
            'family_name': 'family_name',
            'id': 'api_id'
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
        return self._data

    objects = UserManager()

    class Meta:
        db = settings.DEFAULT_DATABASE


class SocialAuth(mongo.Model):
    provider = mongo.CharField(max_length=32, unique=True, db_index=True)
    uid = mongo.CharField(max_length=255, unique=True, db_index=True)
    extra_data = mongo.DictField()

    class Meta:
        abstract = True


class SocialAuthForm(forms.ModelForm):
    class Meta:
        model = SocialAuth
        fields = ['uid', 'provider']


class UserData(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)
    email = mongo.EmailField(max_length=36, db_index=True, unique=True, null=False)
    username = mongo.CharField(max_length=256, db_index=True, unique=True, null=False)

    avatar_url = mongo.CharField(max_length=36)
    given_name = mongo.CharField(max_length=256, null=False)
    family_name = mongo.CharField(max_length=256, null=False)
    full_name = mongo.CharField(max_length=256, null=False)

    # Social Auth fields
    social_auth = mongo.ArrayField(
        model_container=SocialAuth,
        model_form_class=SocialAuthForm,
        default=[]
    )

    objects = mongo.DjongoManager()

    class Meta:
        db_table = 'user_data'
        db = settings.MONGO_DATABASE
