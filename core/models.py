from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.urls import reverse_lazy
from django.utils import timezone
from django import forms
import djongo.models as mongo
from djongo.models.json import JSONField
from users.models import UserData
from _common import utils
from clients import google_client


GOOGLE_CLIENT = google_client.GoogleClient()


class AbstractDocument(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True)
    created_by = mongo.ForeignKey(UserData, on_delete=mongo.CASCADE, null=False)
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


class Article(AbstractDocument):
    class STATUSES(mongo.TextChoices):
        DELETED = 'DL', _('Delete')
        DRAFT = 'DR', _('Draft')
        PUBLISHED = 'PB', _('Publish')
        UNPUBLISHED = 'UP', _('Unpublish')

    title = mongo.CharField(max_length=256, db_index=True)
    slug = mongo.SlugField(unique=True)
    content = mongo.TextField(null=True)
    file_id = mongo.TextField(null=True)
    revision_id = mongo.TextField(null=True)
    status = mongo.CharField(max_length=2, choices=STATUSES.choices, default=STATUSES.DRAFT)
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

    def add_to_google(self):
        access_token = self.created_by.get_access_token()
        result = GOOGLE_CLIENT.add_document(access_token, self.title)
        self.file_id = result['document_id']
        self.revision_id = result['revision_id']

    def update_from_google(self):
        access_token = self.created_by.get_access_token()
        result = GOOGLE_CLIENT.get_document(access_token, self.file_id)
        self.revision_id = result['revision_id']
        self.content = result['html_content']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = utils.unique_slug_generator(self)
            self.add_log(ArticleHistory.STATUSES.ADDED)
            self.add_to_google()
        else:
            self.add_log(ArticleHistory.STATUSES.UPDATED)
            self.update_from_google()

        super(Article, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse_lazy('article:read', kwargs={'slug': self.slug})

    class Meta:
        db_table = 'core_article'
        db = settings.MONGO_DATABASE
