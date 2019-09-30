# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-08 11:58


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0015_1_add_fk_to_document_id'),
        ('meeting', '0014_auto_20190426_0305'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessionpresentation',
            name='document2',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document', to_field=b'id'),
        ),
        migrations.AlterField(
            model_name='sessionpresentation',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='old_sesspres', to='doc.Document', to_field=b'name'),
        ),
    ]