from django.utils.translation import gettext_lazy as _
import djongo.models as mongo
from django import forms
from users.models import UserData
from _common import utils


class AbstractDocument(mongo.Model):
    id = mongo.CharField(max_length=36, db_column='_id', primary_key=True, default=utils.generate_uuid)
    created_by = mongo.ForeignKey(UserData, on_delete=mongo.CASCADE, null=False)
    created_on = mongo.DateTimeField(auto_now_add=True)
    updated_on = mongo.DateTimeField(auto_now=True)

    objects = mongo.DjongoManager()

    class Meta:
        abstract = True


class ArticleHistory(mongo.Model):
    created_on = mongo.DateTimeField(auto_now_add=True)
    action = mongo.TextField() # Add more fields and details later

    class Meta:
        abstract = True


class ArticleHistoryForm(forms.ModelForm):
    class Meta:
        model = ArticleHistory
        fields = ('action', )


class Article(AbstractDocument):
    class STATUSES(mongo.TextChoices):
        DELETED = 'DL', _('Draft')
        DRAFT = 'DR', _('Deleted')
        PUBLISHED = 'PB', _('Published')

    title = mongo.CharField(max_length=256, db_index=True)
    slug = mongo.CharField(max_length=256, db_index=True)
    content = mongo.TextField()
    status = mongo.CharField(max_length=2, choices=STATUSES.choices, default=STATUSES.DRAFT)
    history = mongo.ArrayField(
        model_container=ArticleHistory,
        model_form_class=ArticleHistoryForm,
    )
