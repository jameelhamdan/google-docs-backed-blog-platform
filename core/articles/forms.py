from django import forms
from core import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field


class AddArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(models.Category.objects.filter(is_active=True), required=True)

    class Meta:
        model = models.Article
        fields = ('title', 'category', 'content', 'desc', 'status')

    def __init__(self, *args, **kwargs):
        super(AddArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-12'),
                Field('category', wrapper_class='col-md-6'),
                Field('status', wrapper_class='col-md-6'),
                Field('desc', wrapper_class='col-md-12'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Update', css_class='btn-primary', css_id='submit-button'),
                css_class='form-row'
            ),
            Div(
                Field('content', wrapper_class='col-md-12'),
                css_class='form-row mt-1'
            ),
        )


class ChangeArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(models.Category.objects.filter(is_active=True), required=True)

    class Meta:
        model = models.Article
        fields = ('title', 'category', 'content', 'desc', 'status')

    def __init__(self, *args, **kwargs):
        super(ChangeArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-12'),
                Field('category', wrapper_class='col-md-6'),
                Field('status', wrapper_class='col-md-6'),
                Field('desc', wrapper_class='col-md-12'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Update', css_class='btn-primary', css_id='submit-button'),
                css_class='form-row'
            ),
            Div(
                Field('content', wrapper_class='col-md-12'),
                css_class='form-row editor-wrapper'
            ),
        )
