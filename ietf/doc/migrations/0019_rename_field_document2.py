# Copyright The IETF Trust 2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-21 05:31


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0018_remove_old_document_field'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentauthor',
            options={'ordering': ['document', 'order']},
        ),
        migrations.RemoveIndex(
            model_name='docevent',
            name='doc_doceven_type_ac7748_idx',
        ),
        migrations.RenameField(
            model_name='docalias',
            old_name='document2',
            new_name='document',
        ),
        migrations.RenameField(
            model_name='docevent',
            old_name='doc2',
            new_name='doc',
        ),
        migrations.RenameField(
            model_name='dochistory',
            old_name='doc2',
            new_name='doc',
        ),
        migrations.RenameField(
            model_name='documentauthor',
            old_name='document2',
            new_name='document',
        ),
        migrations.RenameField(
            model_name='documenturl',
            old_name='doc2',
            new_name='doc',
        ),
        migrations.RenameField(
            model_name='relateddochistory',
            old_name='target2',
            new_name='target',
        ),
        migrations.RenameField(
            model_name='relateddocument',
            old_name='source2',
            new_name='source',
        ),
        migrations.RenameField(
            model_name='relateddocument',
            old_name='target2',
            new_name='target',
        ),
        migrations.AddIndex(
            model_name='docevent',
            index=models.Index(fields=['type', 'doc'], name='doc_doceven_type_43e53e_idx'),
        ),
        # Add back the m2m field we removed in 0018_...
        migrations.AddField(
            model_name='document',
            name='formal_languages',
            field=models.ManyToManyField(blank=True, help_text=b'Formal languages used in document', to='name.FormalLanguageName'),
        ),
        migrations.AddField(
            model_name='document',
            name='states',
            field=models.ManyToManyField(blank=True, to='doc.State'),
        ),
        migrations.AddField(
            model_name='document',
            name='tags',
            field=models.ManyToManyField(blank=True, to='name.DocTagName'),
        ),
    ]
