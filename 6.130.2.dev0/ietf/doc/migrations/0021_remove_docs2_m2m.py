# Copyright The IETF Trust 2019-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-30 03:36


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0020_copy_docs_m2m_table'),
    ]

    operations = [
        # Get rid of the explicit m2m tables which we needed only to be
        # able to convert from Document.name to Document.id
        migrations.RemoveField(
            model_name='documentlanguages',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documentlanguages',
            name='formallanguagename',
        ),
        migrations.RemoveField(
            model_name='documentstates',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documentstates',
            name='state',
        ),
        migrations.RemoveField(
            model_name='documenttags',
            name='doctagname',
        ),
        migrations.RemoveField(
            model_name='documenttags',
            name='document',
        ),
        migrations.RemoveField(
            model_name='document',
            name='formal_languages2',
        ),
        migrations.RemoveField(
            model_name='document',
            name='states2',
        ),
        migrations.RemoveField(
            model_name='document',
            name='tags2',
        ),
        migrations.DeleteModel(
            name='DocumentLanguages',
        ),
        migrations.DeleteModel(
            name='DocumentStates',
        ),
        migrations.DeleteModel(
            name='DocumentTags',
        ),
    ]