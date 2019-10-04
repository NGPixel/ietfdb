# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.25 on 2019-10-04 12:12
from __future__ import unicode_literals

from django.db import migrations

def forward(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    Recipient = apps.get_model('mailtrigger','Recipient')

    ietf_last_call = Recipient.objects.create(
        slug = 'ietf_last_call',
        desc = 'The IETF Last Call list',
        template = 'last-call@ietf.org'
    )
    ietf_general = Recipient.objects.get(slug='ietf_general')

    review_completed_triggers = MailTrigger.objects.filter(slug__startswith='review_completed')
    
    for trigger in review_completed_triggers:
        trigger.cc.remove(ietf_general)
        trigger.cc.add(ietf_last_call)

def reverse(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger','MailTrigger')
    Recipient = apps.get_model('mailtrigger','Recipient')

    ietf_general = Recipient.objects.get(slug='ietf_general')
    ietf_last_call = Recipient.objects.get(slug='ietf_last_call')

    review_completed_triggers = MailTrigger.objects.filter(slug__startswith='review_completed')

    for trigger in review_completed_triggers:
        trigger.cc.remove(ietf_last_call)
        trigger.cc.add(ietf_general)

    ietf_last_call.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0009_custom_review_complete_mailtriggers'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
