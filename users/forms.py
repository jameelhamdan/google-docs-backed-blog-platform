from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import forms as auth_forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True
    )

    def clean_password(self):
        password = self.cleaned_data['password']
        auth_forms.password_validation.validate_password(password)
        return password

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_show_labels = False
        self.helper.layout = Layout(
            Div(
                Field('email', wrapper_class='col-md-12', placeholder=_('Email')),
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
