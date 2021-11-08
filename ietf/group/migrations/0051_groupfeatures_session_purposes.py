# Copyright The IETF Trust 2021 All Rights Reserved

# Generated by Django 2.2.24 on 2021-09-26 11:29

from django.db import migrations
import ietf.group.models
import ietf.name.models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0050_populate_groupfeatures_agenda_filter_type'),
        ('name', '0034_sessionpurposename'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupfeatures',
            name='session_purposes',
            field=jsonfield.fields.JSONField(default=[], help_text='Allowed session purposes for this group type', max_length=256, validators=[ietf.group.models.JSONForeignKeyListValidator(ietf.name.models.SessionPurposeName)]),
        ),
    ]