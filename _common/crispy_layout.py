from django.template import Template
from crispy_forms.layout import HTML
from crispy_forms.utils import TEMPLATE_PACK


class BaseHTML(HTML):
    def __init__(self, html, extra_context):
        self.html = html
        self.extra_context = extra_context

    extra_context = {}

    def get_content_data(self):
        context = {}
        context.update(self.extra_context)
        return context

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK, **kwargs):
        context.update(self.get_content_data())
        return Template(str(self.html)).render(context)


class FormAnchorButton(BaseHTML):
    html = '<a {%if css_id %} id="{{ css_id }}" {% endif %} href="{{ url }}" class="btn btn--sm custom-form-button {{css_class}}"><span class="btn__text">{{inner_html|safe}}</span></a>'

    def __init__(self, url, inner_html, **kwargs):
        context = {
            'inner_html': inner_html,
            'url': url
        }
        context.update(kwargs)
        super().__init__(self.html, context)