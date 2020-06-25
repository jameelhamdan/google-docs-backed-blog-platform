from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.urls import reverse_lazy
from users.models import User
from core import models
from _common import mixins


class ProfileView(mixins.PageMixin, generic.DetailView):
    """
    Any Profile View
    """
    template_name = 'profile/main.html'
    queryset = User.objects.all()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'

    title_template = _('%s Profile')
    title_object = True
    title_object_attribute = 'name'

    extra_context = {
        'ARTICLE_STATUSES': models.Article.STATUSES,
    }

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        context['is_manager'] = is_manager = self.request.user.pk == self.object.pk

        # TODO: Paginate this
        articles_queryset = self.object.data.added_articles.select_related('category')
        if not is_manager:
            articles_queryset.filter(status=models.Article.STATUSES.PUBLISHED)

        context['user_articles'] = articles_queryset
        return context


class MyProfileRedirect(generic.RedirectView):
    """
    Redirect to user profile Login or
    """
    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.request.user.get_absolute_url()
        else:
            return reverse_lazy('users:social_login')
