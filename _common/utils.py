from django.utils.text import slugify
import uuid
import random
import string


def random_str(length=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def generate_uuid(repeat=1):
    final_uuid = ''
    for i in range(0, repeat):
        final_uuid += uuid.uuid4().hex

    return final_uuid


def unique_slug_generator(instance, new_slug=None, field_name='title'):
    """
    This is for a Django project and it assumes your instance
    has a model with a slug field and a title/name character (char) field.
    """
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(getattr(instance, field_name))

    klass = instance.__class__
    qs_exists = klass.objects.filter(slug=slug).exists()
    if qs_exists:
        new_slug = f'{slug}-{random_str(4)}'
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug
