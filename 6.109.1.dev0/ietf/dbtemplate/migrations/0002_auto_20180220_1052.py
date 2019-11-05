# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from __future__ import absolute_import, print_function, unicode_literals

from django.db import migrations
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
        ('name', '0001_initial'),
        ('dbtemplate', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='dbtemplate',
            name='group',
            field=ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group'),
        ),
        migrations.AddField(
            model_name='dbtemplate',
            name='type',
            field=ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.DBTemplateTypeName'),
        ),
    ]
