from django.utils.translation import gettext_lazy as _
from django.views import generic
from django.urls import reverse_lazy
from core.models import Article
from . import forms
from _common import mixins


class AddArticleView(mixins.PageMixin, generic.CreateView):
    template_name = 'article/add.html'
    form_class = forms.AddArticleForm
    title = _('Add Article')

    def get_success_url(self):
        return reverse_lazy('articles:change', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.created_by_id = self.request.user.pk
        instance.save()
        return super(AddArticleView, self).form_valid(form)


class ChangeArticleView(mixins.PageMixin, generic.UpdateView):
    template_name = 'article/add.html'
    form_class = forms.ChangeArticleForm
    queryset = Article.objects.all()
    title = _('Change Article')

    def get_success_url(self):
        return reverse_lazy('articles:change', kwargs={'pk': self.object.pk})
