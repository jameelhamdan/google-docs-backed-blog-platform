from django.conf import settings
from django.views import generic
from django.contrib.auth import login, logout, views as auth_views
from .social.backend import GoogleOAuthClient
from . import models, forms


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


class LoginView(auth_views.LoginView):
    http_method_names = ['post']
    form_class = forms.LoginForm


class RegisterView(generic.edit.BaseFormView):
    http_method_names = ['post']
    form_class = forms.RegisterForm

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        username = None

        return models.User.objects.create_user(username, email, password, provider='default')
