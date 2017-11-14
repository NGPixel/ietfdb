# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-07-20 06:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0025_add-important-dates'),
        ('meeting', '0052_floorplan_short'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportantDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('meeting', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.Meeting')),
                ('name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='name.ImportantDateName')),
            ],
            options={'ordering': ['-meeting','date']},
        ),
    ]
