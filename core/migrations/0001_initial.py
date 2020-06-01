# Generated by Django 3.0.6 on 2020-06-01 18:12

import _common.utils
import core.models
from django.db import migrations, models
import django.db.models.deletion
import djongo.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_userdata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.CharField(db_column='_id', default=_common.utils.generate_uuid, max_length=36, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('updated_on', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(db_index=True, max_length=256)),
                ('slug', models.CharField(db_index=True, max_length=256)),
                ('content', models.TextField()),
                ('status', models.CharField(choices=[('DL', 'Draft'), ('DR', 'Deleted'), ('PB', 'Published')], default='DR', max_length=2)),
                ('history', djongo.models.fields.ArrayField(model_container=core.models.ArticleHistory, model_form_class=core.models.ArticleHistoryForm)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.UserData')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]