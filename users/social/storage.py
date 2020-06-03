import base64
import six
from django.contrib.auth import get_user_model
from djongo.models import DictField, IntegerField, CharField, EmailField, BooleanField
from djongo.database import OperationalError
from social_core.storage import UserMixin, AssociationMixin, NonceMixin, CodeMixin, PartialMixin, BaseStorage as _BaseStorage


UNUSABLE_PASSWORD = '!'


class SocialUserMixin(UserMixin):
    """Social Auth association model"""
    user = None

    def str_id(self):
        return str(self.id)

    @classmethod
    def user_model(cls):
        return get_user_model()

    @staticmethod
    def user_data_model():
        return get_user_model().get_data_model()

    @staticmethod
    def social_auth_model():
        return get_user_model().get_social_auth_model()

    @classmethod
    def get_social_auth_for_user(cls, user, provider=None, id=None):
        user_data = user.data
        return user_data.social_auth

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        if not isinstance(type(uid), six.string_types):
            uid = str(uid)

        social_auth = cls.social_auth_model()(uid=uid, provider=provider)

        user_data = user.data
        user_data.social_auth.append(social_auth)
        user_data.save()
        return social_auth

    @classmethod
    def username_max_length(cls):
        return 254  # the username is an email, it shouldn't change from 254

    @classmethod
    def username_field(cls):
        return getattr(cls.user_model(), 'USERNAME_FIELD', 'username')

    @classmethod
    def create_user(cls, *args, **kwargs):
        kwargs['password'] = UNUSABLE_PASSWORD
        if 'email' in kwargs:
            # Empty string makes email regex validation fail
            kwargs['email'] = kwargs['email'] or None
        return cls.user_model().objects.create(*args, **kwargs)

    @classmethod
    def allowed_to_disconnect(cls, user, backend_name, association_id=None):
        user_data = user.data
        qs = user_data.social_auth

        if association_id is not None:
            qs = qs.filter(id__ne=association_id)
        else:
            qs = qs.filter(provider__ne=backend_name)

        if hasattr(user, 'has_usable_password'):
            valid_password = user.has_usable_password()
        else:
            valid_password = True

        return valid_password or qs.count() > 0

    @classmethod
    def changed(cls, user):
        user.save()

    def set_extra_data(self, extra_data=None):
        if super(SocialUserMixin, self).set_extra_data(extra_data):
            self.save()

    @classmethod
    def disconnect(cls, entry):
        entry.delete()

    @classmethod
    def user_exists(cls, *args, **kwargs):
        """
        Return True/False if a User instance exists with the given arguments.
        Arguments are directly passed to filter() manager method.
        """
        if 'username' in kwargs:
            kwargs[cls.username_field()] = kwargs.pop('username')
        return cls.user_model().objects.filter(*args, **kwargs).count() > 0

    @classmethod
    def get_username(cls, user):
        return getattr(user, cls.username_field(), None)

    @classmethod
    def get_user(cls, pk):
        try:
            return cls.user_model().objects.get(id=pk)
        except cls.user_model().DoesNotExist:
            return None

    @classmethod
    def get_users_by_email(cls, email):
        return cls.user_model().objects.filter(email__iexact=email)

    @classmethod
    def get_social_auth(cls, provider, uid):
        if not isinstance(uid, six.string_types):
            uid = str(uid)

        try:
            qs = cls.user_data_model().objects
            return qs.get(social_auth={'provider': provider, 'uid': uid})
        except cls.user_data_model().DoesNotExist:
            return None


class SocialNonceMixin(NonceMixin):
    """One use numbers"""
    server_url = CharField(max_length=255)
    timestamp = IntegerField()
    salt = CharField(max_length=40)

    @classmethod
    def use(cls, server_url, timestamp, salt):
        raise NotImplemented('Something has attempted to OpenID')


class SocialAssociationMixin(AssociationMixin):
    """OpenId account association"""
    server_url = CharField(max_length=255)
    handle = CharField(max_length=255)
    secret = CharField(max_length=255)  # Stored base64 encoded
    issued = IntegerField()
    lifetime = IntegerField()
    assoc_type = CharField(max_length=64)

    @classmethod
    def store(cls, server_url, association):
        raise NotImplemented('Something has attempted to OpenID')

    @classmethod
    def get(cls, *args, **kwargs):
        raise NotImplemented('Something has attempted to OpenID')

    @classmethod
    def remove(cls, ids_to_delete):
        raise NotImplemented('Something has attempted to OpenID')


class SocialCodeMixin(CodeMixin):
    email = EmailField()
    code = CharField(max_length=32)
    verified = BooleanField(default=False)

    @classmethod
    def get_code(cls, code):
        raise NotImplemented('Something has attempted to OpenID')


class SocialPartialMixin(PartialMixin):
    token = CharField(max_length=32)
    data = DictField()
    extra_data = DictField()
    next_step = IntegerField()
    backend = CharField(max_length=32)

    @classmethod
    def load(cls, token):
        raise NotImplemented('Something has attempted to OpenID')

    @classmethod
    def destroy(cls, token):
        raise NotImplemented('Something has attempted to OpenID')


class BaseStorage(_BaseStorage):
    user = SocialUserMixin
    nonce = SocialNonceMixin
    association = SocialAssociationMixin
    code = SocialCodeMixin
    partial = SocialPartialMixin

    @classmethod
    def is_integrity_error(cls, exception):
        return exception.__class__ is OperationalError and 'E11000' in exception.message
