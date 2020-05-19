# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-10 13:47


from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('name', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgendaTypeName',
            fields=[
                ('slug', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('desc', models.TextField(blank=True)),
                ('used', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['order', 'name'],
                'abstract': False,
            },
        ),
    ]
