# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-20 09:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0017_make_document_id_primary_key'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentauthor',
            options={'ordering': ['document2', 'order']},
        ),
        migrations.RemoveIndex(
            model_name='docevent',
            name='doc_doceven_type_43e53e_idx',
        ),
        migrations.RemoveField(
            model_name='docalias',
            name='document',
        ),
        migrations.RemoveField(
            model_name='docevent',
            name='doc',
        ),
        migrations.RemoveField(
            model_name='dochistory',
            name='doc',
        ),
        migrations.RemoveField(
            model_name='documentauthor',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documenturl',
            name='doc',
        ),
        migrations.RemoveField(
            model_name='relateddochistory',
            name='target',
        ),
        migrations.RemoveField(
            model_name='relateddocument',
            name='source',
        ),
        migrations.RemoveField(
            model_name='relateddocument',
            name='target',
        ),
        migrations.AddIndex(
            model_name='docevent',
            index=models.Index(fields=[b'type', b'doc2'], name='doc_doceven_type_ac7748_idx'),
        ),
        # The following 9 migrations are related to the m2m fields on Document
        # Remove the intermediary model field pointing to Document.name
        migrations.RemoveField(
            model_name='documentlanguages',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documentstates',
            name='document',
        ),
        migrations.RemoveField(
            model_name='documenttags',
            name='document',
        ),
        # Rename the intermediary model field pointing to Document.id, to
        # match the implicit m2m table
        migrations.RenameField(
            model_name='documentlanguages',
            old_name='document2',
            new_name='document',
        ),
        migrations.RenameField(
            model_name='documentstates',
            old_name='document2',
            new_name='document',
        ),
        migrations.RenameField(
            model_name='documenttags',
            old_name='document2',
            new_name='document',
        ),
        # Alter the fields to point to Document.pk instead of Document.name
        migrations.AlterField(
            model_name='documentlanguages',
            name='document',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
        migrations.AlterField(
            model_name='documentstates',
            name='document',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
        migrations.AlterField(
            model_name='documenttags',
            name='document',
            field=ietf.utils.models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='doc.Document'),
        ),
        # Remove the implicit m2m tables which point to Document.name
        migrations.RemoveField(
            model_name='document',
            name='formal_languages',
        ),
        migrations.RemoveField(
            model_name='document',
            name='states',
        ),
        migrations.RemoveField(
            model_name='document',
            name='tags',
        ),
        # Next (in a separate migration, in order to commit the above before
        # we proceed) we'll create the implicit m2m tables again, this time
        # pointing to Document.id since that's now the primary key.
    ]
