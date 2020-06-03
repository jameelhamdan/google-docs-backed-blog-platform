from django.conf import settings
from ..models import UserData


def user_data(strategy, details, backend, user=None, *args, **kwargs):
    """Update user details using data from provider."""
    if not user:
        return

    changed = False  # flag to track changes

    # Default protected user fields (username, id, pk and email) can be ignored
    # by setting the SOCIAL_AUTH_NO_DEFAULT_PROTECTED_USER_FIELDS to True
    if strategy.setting('NO_DEFAULT_PROTECTED_USER_FIELDS') is True:
        protected = ()
    else:
        protected = (
            'username', 'id', 'pk', 'email', 'password', 'is_active', 'provider',
            'is_staff', 'is_superuser', 'created_on', 'updated_on', 
        )

    protected = protected + tuple(strategy.setting('PROTECTED_USER_FIELDS', []))

    # Update user model attributes with the new data sent by the current
    # provider. Update on some attributes is disabled by default, for
    # example username and id fields. It's also possible to disable update
    # on fields defined in SOCIAL_AUTH_PROTECTED_USER_FIELDS.
    field_mapping = strategy.setting('USER_FIELD_MAPPING', {}, backend)
    for name, value in details.items():
        # Convert to existing user field if mapping exists
        name = field_mapping.get(name, name)
        if value is None or not hasattr(user, name) or name in protected:
            continue

        current_value = getattr(user, name, None)
        if current_value == value:
            continue

        changed = True
        setattr(user, name, value)

    json_changed = False
    json_field_mapping = UserData.FIELD_MAPPING[backend.name]

    user_data = user.data
    for name, value in kwargs['response'].items():
        # Convert to existing user field if mapping exists
        name = json_field_mapping.get(name, name)
        if value is None or not hasattr(user_data, name) or name in protected:
            continue

        current_value = getattr(user_data, name, None)
        if current_value == value:
            continue

        json_changed = True
        setattr(user_data, name, value)

    if changed:
        strategy.storage.user.changed(user)

    if json_changed:
        user_data.save()
