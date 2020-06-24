from django.core import exceptions
import djongo.models as mongo
from urllib.parse import unquote
from .widgets import TextEditorJsWidget, JSONEditorJsWidget
import json
from _common import utils


class JSONEditorJSField(mongo.JSONField):
    def __init__(self, *args, **kwargs):
        super(JSONEditorJSField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        if not value or value == '':
            return None

        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            raise exceptions.ValidationError

        utils.parse_editor_js_data(value)

        return super(JSONEditorJSField, self).clean(value, model_instance)

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = JSONEditorJsWidget()
        return super(JSONEditorJSField, self).formfield(*args, **kwargs)


class TextEditorJSField(mongo.Field):
    def __init__(self, *args, **kwargs):
        super(TextEditorJSField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def clean(self, value, model_instance):
        if value is not None:
            value = unquote(super(TextEditorJSField, self).clean(value, model_instance))
            utils.parse_editor_js_data(value)
            return value
        else:
            return None

    def formfield(self, *args, **kwargs):
        kwargs['widget'] = TextEditorJsWidget()
        return super(TextEditorJSField, self).formfield(*args, **kwargs)
