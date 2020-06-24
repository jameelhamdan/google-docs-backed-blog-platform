from django.utils.translation import gettext_lazy as _
from django.views import generic
from users.models import User
from _common import mixins


class ProfileView(mixins.PageMixin, generic.DetailView):
    template_name = 'profile/main.html'
    queryset = User.objects.all()
    slug_field = 'username'
    slug_url_kwarg = 'username'
    context_object_name = 'user'

    title_template = _('%s Profile')
    title_object = True
    title_object_attribute = 'name'

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileView, self).get_context_data(**kwargs)

        # TODO: Paginate this
        context['user_articles'] = self.object.data.added_articles.select_related('category')

        return context
