from django.conf import settings
from django.views import generic

from django.contrib.auth import logout


class LogoutView(generic.RedirectView):
    url = settings.LOGOUT_REDIRECT_URL

    def get_redirect_url(self, *args, **kwargs):
        logout(request=self.request)
        return super(LogoutView, self).get_redirect_url(*args, **kwargs)
