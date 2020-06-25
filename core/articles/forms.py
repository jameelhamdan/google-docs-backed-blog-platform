from django import forms
from django.urls import reverse_lazy
from core import models
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from _common.crispy_layout import FormAnchorButton


class AddArticleForm(forms.ModelForm):
    category = forms.ModelChoiceField(models.Category.objects.filter(is_active=True), required=True)

    class Meta:
        model = models.Article
        fields = ('title', 'category', 'content', 'desc')

    def __init__(self, *args, **kwargs):
        super(AddArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-6'),
                Field('category', wrapper_class='col-md-6'),
                Field('desc', wrapper_class='col-md-12'),
                css_class='form-row'
            ),
            Div(
                FormAnchorButton(reverse_lazy('profile:me'), 'Cancel', css_class='btn-warning', css_id='submit-button'),
                Submit('submit', 'Add', css_class='btn-primary', css_id='submit-button'),
                css_class='btn-group col-sm-6 col-md-3'
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

    def save(self, commit=True):
        if commit:
            self.add_log(models.ArticleHistory.STATUSES.UPDATED)

        return super(ChangeArticleForm, self).save(commit)

    def __init__(self, *args, **kwargs):
        super(ChangeArticleForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.include_media = False
        self.helper.layout = Layout(
            Div(
                Field('title', wrapper_class='col-md-6'),
                Field('category', wrapper_class='col-md-6'),
                Field('desc', wrapper_class='col-md-12'),
                css_class='form-row'
            ),
            Div(
                FormAnchorButton(reverse_lazy('profile:me'), 'Cancel', css_class='btn-warning', css_id='submit-button'),
                Submit('submit', 'Save', css_class='btn-primary', css_id='submit-button'),
                css_class='btn-group col-sm-6 col-md-3'
            ),
            Div(
                Field('content', wrapper_class='col-md-12'),
                css_class='form-row mt-1'
            ),
        )
