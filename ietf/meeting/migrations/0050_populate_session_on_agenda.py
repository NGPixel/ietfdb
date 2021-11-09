# Generated by Django 2.2.24 on 2021-10-22 06:58

from django.db import migrations, models


def forward(apps, schema_editor):
    Session = apps.get_model('meeting', 'Session')
    SchedTimeSessAssignment = apps.get_model('meeting', 'SchedTimeSessAssignment')
    # find official assignments that are to private timeslots and fill in session.on_agenda
    private_assignments = SchedTimeSessAssignment.objects.filter(
        models.Q(
            schedule=models.F('session__meeting__schedule')
        ) | models.Q(
            schedule=models.F('session__meeting__schedule__base')
        ),
        timeslot__type__private=True,
    )
    for pa in private_assignments:
        pa.session.on_agenda = False
        pa.session.save()
    # Also update any sessions to match their purpose's default setting (this intentionally
    # overrides the timeslot settings above, but that is unlikely to matter because the
    # purposes will roll out at the same time as the on_agenda field)
    Session.objects.filter(purpose__on_agenda=False).update(on_agenda=False)
    Session.objects.filter(purpose__on_agenda=True).update(on_agenda=True)

def reverse(apps, schema_editor):
    Session = apps.get_model('meeting', 'Session')
    Session.objects.update(on_agenda=True)  # restore all to default on_agenda=True state

class Migration(migrations.Migration):

    dependencies = [
        ('meeting', '0049_session_on_agenda'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
