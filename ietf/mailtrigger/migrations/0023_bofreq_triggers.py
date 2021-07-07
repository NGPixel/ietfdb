# Copyright The IETF Trust 2021 All Rights Reserved
# Generated by Django 2.2.23 on 2021-05-26 07:52

from django.db import migrations

def forward(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    Recipient = apps.get_model('mailtrigger', 'Recipient')

    Recipient.objects.create(slug='bofreq_editors',desc='BOF request editors',template='')
    Recipient.objects.create(slug='bofreq_previous_editors',desc='Editors of the prior version of a BOF request', 
        template='{% for editor in previous_editors %}{{editor.email_address}}{% if not forloop.last %},{% endif %}{% endfor %}')

    Recipient.objects.create(slug='bofreq_responsible',desc='BOF request responsible leadership',template='')
    Recipient.objects.create(slug='bofreq_previous_responsible',desc='BOF request responsible leadership before change', template='')

    mt = MailTrigger.objects.create(slug='bofreq_title_changed',desc='Recipients when the title of a BOF proposal is changed.')
    mt.to.set(Recipient.objects.filter(slug__in=['bofreq_responsible', 'bofreq_editors', 'doc_notify']))

    mt = MailTrigger.objects.create(slug='bofreq_editors_changed',desc='Recipients when the editors of a BOF proposal are changed.')
    mt.to.set(Recipient.objects.filter(slug__in=['bofreq_responsible', 'bofreq_editors', 'bofreq_previous_editors', 'doc_notify']))

    mt = MailTrigger.objects.create(slug='bofreq_responsible_changed',desc='Recipients when the responsible leadership of a BOF proposal are changed.')
    mt.to.set(Recipient.objects.filter(slug__in=['bofreq_responsible', 'bofreq_editors', 'bofreq_previous_responsible', 'doc_notify']))

    mt = MailTrigger.objects.create(slug='bofreq_new_revision', desc='Recipients when a new revision of a BOF request is uploaded.')
    mt.to.set(Recipient.objects.filter(slug__in=['bofreq_responsible', 'bofreq_editors', 'doc_notify']))

def reverse(apps, schema_editor):
    MailTrigger = apps.get_model('mailtrigger', 'MailTrigger')
    Recipient = apps.get_model('mailtrigger', 'Recipient')
    MailTrigger.objects.filter(slug__in=('bofreq_title_changed', 'bofreq_editors_changed', 'bofreq_new_revision', 'bofreq_responsible_changed')).delete()
    Recipient.objects.filter(slug__in=('bofreq_editors', 'bofreq_previous_editors')).delete()
    Recipient.objects.filter(slug__in=('bofreq_responsible', 'bofreq_previous_responsible')).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('mailtrigger', '0022_add_doc_external_resource_change_requested'),
    ]

    operations = [
        migrations.RunPython(forward,reverse)
    ]
