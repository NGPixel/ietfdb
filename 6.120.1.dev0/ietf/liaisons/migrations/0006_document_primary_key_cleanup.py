# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-06-10 03:47


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('liaisons', '0005_rename_field_document2'),
    ]

    operations = [
        migrations.AlterField(
            model_name='liaisonstatementattachment',
            name='document',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
    ]
