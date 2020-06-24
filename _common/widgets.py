from django.forms import widgets
from django.template.loader import render_to_string
import json


class TextEditorJsWidget(widgets.TextInput):
    class Media:
        js = (
            'js/editorjs/editor.js',
            'js/editorjs/list.js',
            'js/editorjs/code.js',
            'js/editorjs/inline-code.js',
            'js/editorjs/delimiter.js',
            'js/editorjs/header.js',
            'js/editorjs/embed.js',
            'js/editorjs/image.js',
            'js/editorjs/qoute.js',
            'js/editorjs/link.js',
            'js/editorjs/table.js',
            'js/editorjs/marker.js',
            'js/editorjs_field.js',
        )

        css = {'all': ('css/editorjs_field.css', )}

    def __init__(self, *args, **kwargs):
        super(TextEditorJsWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, **kwargs):
        ctx = {
            'name': name,
            'id': kwargs['attrs']['id'],
            'value': value
        }

        return render_to_string('widgets/editorjs_widget.tpl', ctx)


class JSONEditorJsWidget(TextEditorJsWidget):
    def render(self, name, value, **kwargs):
        value = json.dumps(value)
        return super(JSONEditorJsWidget, self).render(name, value, **kwargs)
