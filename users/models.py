from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.utils import timezone
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
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
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

    def get_data(self):
        return UserData.objects.get(pk=self.pk)

    objects = UserManager()

    class Meta:
        db = settings.DEFAULT_DATABASE


class UserData(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True)
    api_id = mongo.CharField(max_length=36, null=True)
    provider = mongo.CharField(max_length=128, null=True)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)
    email = mongo.EmailField(max_length=36, db_index=True, unique=True, null=False)
    username = mongo.CharField(max_length=256, db_index=True, unique=True, null=False)

    avatar_url = mongo.CharField(max_length=36)
    given_name = mongo.CharField(max_length=256, null=False)
    family_name = mongo.CharField(max_length=256, null=False)
    full_name = mongo.CharField(max_length=256, null=False)
    birth_date = mongo.DateField(null=False)

    objects = mongo.DjongoManager()
    FIELD_MAPPING = {
        'email': 'email',
        'username': 'username',
        'picture': 'avatar_url',
        'name': 'full_name',
        'given_name': 'given_name',
        'family_name': 'family_name',
        'id': 'api_id'
    }

    class Meta:
        db_table = 'user_data'
        db = settings.MONGO_DATABASE
