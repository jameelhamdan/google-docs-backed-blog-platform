from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import forms as auth_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from . import models
from _common import validators


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    given_name = forms.CharField(required=True, min_length=3, max_length=128, validators=[validators.alphanumeric_validator])
    family_name = forms.CharField(required=True, min_length=3, max_length=128, validators=[validators.alphanumeric_validator])
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        auth_forms.password_validation.validate_password(password)
        return password

    def clean_email(self):
        if models.User.objects.filter(email=self.cleaned_data['email']).exists():
            raise forms.ValidationError(_('This email is already registered.'), 'email_exists')
        return self.cleaned_data['email']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('email', wrapper_class='col-md-12', placeholder=_('Email')),
                Field('given_name', wrapper_class='col-md-6', placeholder=_('Given Name')),
                Field('family_name', wrapper_class='col-md-6', placeholder=_('Family Name')),
                Field('password', wrapper_class='col-md-12', placeholder=_('Password')),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Register', css_class='btn--primary type--uppercase', wrapper_class='col-12', css_id='submit-button'),
                css_class='form-row'
            ),
        )


class LoginForm(auth_forms.AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('username', wrapper_class='col-12', placeholder=_('Email')),
                Field('password', wrapper_class='col-12', placeholder=_('Password')),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Login', css_class='btn--primary type--uppercase', wrapper_class='col-12', css_id='submit-button'),
                css_class='form-row'
            ),
        )
