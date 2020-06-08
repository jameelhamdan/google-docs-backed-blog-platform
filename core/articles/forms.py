from django import forms
from core.models import Article
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field


class AddArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'slug', )

    def __init__(self, *args, **kwargs):
        super(AddArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-6'),
                Field('slug', wrapper_class='col-md-6'),
                css_class='form-row')
        )

        self.helper.add_input(Submit('submit', 'Add', css_class='btn-primary'))
        self.helper.form_method = 'POST'


class ChangeArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ('title', 'slug', )

    def __init__(self, *args, **kwargs):
        super(ChangeArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-6'),
                Field('slug', wrapper_class='col-md-6'),
                css_class='form-row')
        )
        self.helper.add_input(Submit('submit', 'Update', css_class='btn-primary'))
        self.helper.form_method = 'POST'
