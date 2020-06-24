from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from django import forms
import djongo.models as mongo
from djongo.models.json import JSONField
from users.models import UserData
from _common import utils, fields


class AbstractDocument(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)

    objects = mongo.DjongoManager()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.pk = utils.generate_uuid()
        super(AbstractDocument, self).save(*args, **kwargs)

    class Meta:
        abstract = True


class ArticleHistory(mongo.Model):
    class STATUSES(mongo.TextChoices):
        DELETED = 'DL', _('Delete')
        DRAFT = 'DR', _('Draft')
        PUBLISHED = 'PB', _('Publish')
        UNPUBLISHED = 'UP', _('Unpublish')
        ADDED = 'AD', _('Added')
        UPDATED = 'UD', _('Updated')

    action = mongo.CharField(max_length=2, choices=STATUSES.choices)
    created_on = mongo.DateTimeField()
    extra_data = JSONField(default={})

    class Meta:
        abstract = True


class ArticleHistoryForm(forms.ModelForm):
    class Meta:
        model = ArticleHistory
        fields = ('action', 'extra_data', 'created_on')


class Category(mongo.Model):
    slug = mongo.SlugField(unique=True, db_column='_id', primary_key=True)
    name = mongo.CharField(max_length=64)
    is_active = mongo.BooleanField(default=False)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = utils.unique_slug_generator(self, field_name='name')
        super(Category, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'core_category'
        db = settings.MONGO_DATABASE
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'


class Article(AbstractDocument):
    class STATUSES(mongo.TextChoices):
        DELETED = 'DL', _('Delete')
        DRAFT = 'DR', _('Draft')
        PUBLISHED = 'PB', _('Publish')
        UNPUBLISHED = 'UP', _('Unpublish')

    title = mongo.CharField(max_length=128, verbose_name=_('Title'), db_index=True, blank=False)
    slug = mongo.SlugField(unique=True)
    desc = mongo.TextField(verbose_name=_('Short Description'), max_length=256, blank=False, null=True)
    category = mongo.ForeignKey(Category, on_delete=mongo.PROTECT, verbose_name=_('Category'), related_name='articles', null=False)
    content = fields.TextEditorJSField(verbose_name=_('Content'), blank=False)
    status = mongo.CharField(max_length=2, verbose_name=_('Status'), choices=STATUSES.choices, default=STATUSES.DRAFT)
    created_by = mongo.ForeignKey(UserData, on_delete=mongo.PROTECT, related_name='added_articles', null=False)
    history = mongo.ArrayField(
        model_container=ArticleHistory,
        model_form_class=ArticleHistoryForm,
        default=[]
    )

    def add_log(self, action, extra_data=dict(), save=False):
        self.history.append(
            {
                'action': action,
                'extra_data': extra_data,
                'created_on': timezone.now()
            }
        )

        if save:
            self.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = utils.unique_slug_generator(self)
            self.add_log(ArticleHistory.STATUSES.ADDED)
        else:
            self.add_log(ArticleHistory.STATUSES.UPDATED)

        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('articles:read', kwargs={'slug': self.slug})

    def get_content_html(self):
        return utils.parse_editor_js_data(self.content)

    class Meta:
        db_table = 'core_article'
        db = settings.MONGO_DATABASE
