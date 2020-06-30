# Copyright The IETF Trust 2020, All Rights Reserved

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0012_update_constraintname_order_and_label'),
    ]

    def add_rescheduled_session_status_name(apps, schema_editor):
        SessionStatusName = apps.get_model('name', 'SessionStatusName')
        SessionStatusName.objects.get_or_create(
            slug='resched',
            name="Rescheduled",
        )

    def noop(apps, schema_editor):
        pass

    operations = [
        migrations.RunPython(add_rescheduled_session_status_name, noop, elidable=True),
    ]
