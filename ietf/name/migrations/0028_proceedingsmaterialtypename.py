# Copyright The IETF Trust 2021 All Rights Reserved

# Generated by Django 2.2.24 on 2021-07-26 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0027_add_bofrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProceedingsMaterialTypeName',
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
