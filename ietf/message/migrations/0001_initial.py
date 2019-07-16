# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from __future__ import absolute_import, print_function, unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import email.utils
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0001_initial'),
        ('name', '0001_initial'),
        ('person', '0001_initial'),
        ('doc', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnnouncementFrom',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=255)),
                ('group', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('name', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.RoleName')),
            ],
            options={
                'verbose_name_plural': 'Announcement From addresses',
            },
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('subject', models.CharField(max_length=255)),
                ('frm', models.CharField(max_length=255)),
                ('to', models.CharField(max_length=1024)),
                ('cc', models.CharField(blank=True, max_length=1024)),
                ('bcc', models.CharField(blank=True, max_length=255)),
                ('reply_to', models.CharField(blank=True, max_length=255)),
                ('body', models.TextField()),
                ('content_type', models.CharField(blank=True, default=b'text/plain', max_length=255)),
                ('msgid', models.CharField(blank=True, default=email.utils.make_msgid, max_length=255, null=True)),
                ('by', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
                ('related_docs', models.ManyToManyField(blank=True, to='doc.Document')),
                ('related_groups', models.ManyToManyField(blank=True, to='group.Group')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
        migrations.CreateModel(
            name='MessageAttachment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, db_index=True, max_length=255)),
                ('content_type', models.CharField(blank=True, max_length=255)),
                ('encoding', models.CharField(blank=True, max_length=255)),
                ('removed', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('message', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
        ),
        migrations.CreateModel(
            name='SendQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time', models.DateTimeField(default=datetime.datetime.now)),
                ('send_at', models.DateTimeField(blank=True, null=True)),
                ('sent_at', models.DateTimeField(blank=True, null=True)),
                ('note', models.TextField(blank=True)),
                ('by', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
                ('message', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='message.Message')),
            ],
            options={
                'ordering': ['time'],
            },
        ),
    ]
