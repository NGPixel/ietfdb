# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2018-11-02 10:10


from django.db import migrations, models
import ietf.review.models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0004_add_prefix_to_doctypenames'),
        ('review', '0002_unavailableperiod_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='reviewteamsettings',
            name='notify_ad_when',
            field=models.ManyToManyField(related_name='reviewteamsettings_notify_ad_set', to='name.ReviewResultName'),
        ),
        migrations.AlterField(
            model_name='reviewteamsettings',
            name='review_results',
            field=models.ManyToManyField(default=ietf.review.models.get_default_review_results, related_name='reviewteamsettings_review_results_set', to='name.ReviewResultName'),
        ),
    ]
