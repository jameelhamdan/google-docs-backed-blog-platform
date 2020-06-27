from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.views import generic
from django.contrib.auth import login, logout, views as auth_views
from .social.backend import GoogleOAuthClient
from . import models, forms
from _common import mixins


GOOGLE_AUTH_CLIENT = GoogleOAuthClient()


class LogoutView(generic.RedirectView):
    url = settings.LOGOUT_REDIRECT_URL

    def get_redirect_url(self, *args, **kwargs):
        logout(request=self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)


class SocialLoginView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return GOOGLE_AUTH_CLIENT.get_authorization_uri(self.request)


class SocialLoginCompleteView(generic.RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        user_info = GOOGLE_AUTH_CLIENT.get_info_after_complete(self.request)
        user = GOOGLE_AUTH_CLIENT.create_or_update_user(user_info)
        login(self.request, user)
        return settings.LOGIN_REDIRECT_URL


class LoginView(mixins.PageMixin, auth_views.LoginView):
    template_name = 'login.html'
    form_class = forms.LoginForm
    title = _('Login')


class RegisterView(mixins.PageMixin, generic.FormView):
    template_name = 'register.html'
    form_class = forms.RegisterForm
    title = _('Register')

    def get_success_url(self):
        return self.request.user.get_absolute_url()

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        email = cleaned_data['email']
        password = cleaned_data['password']
        given_name = cleaned_data['given_name']
        family_name = cleaned_data['family_name']
        name = f'{given_name} {family_name}'
        username = None

        user = models.User.objects.create_user(username, email, password, given_name=given_name, family_name=family_name, name=name, provider='default')

        # Login user after registration
        login(self.request, user)
        return super(RegisterView, self).form_valid(form)
