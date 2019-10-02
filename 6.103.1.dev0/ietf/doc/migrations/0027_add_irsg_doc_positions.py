# Copyright The IETF Trust 2018-2019, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-08-03 10:09
from __future__ import unicode_literals

from django.db import migrations

# forward, reverse initially copied from migration 0004
def forward(apps, schema_editor):
    State = apps.get_model('doc','State')
    State.objects.create(type_id='draft-stream-irtf',
                         slug='irsg_review',
                         name='IRSG Review',
                         desc='IRSG Review',
                         used=True,
                        )
    BallotPositionName = apps.get_model('name','BallotPositionName')
    # desc, used, order, and blocking all have suitable defaults
    BallotPositionName.objects.create(slug="moretime",
                           name="Need More Time",
                          )
    BallotPositionName.objects.create(slug="notready",
                           name="Not Ready",
                          )

    # Create a new ballot type for IRSG ballot
    # include positions for the ballot type
    BallotType = apps.get_model('doc','BallotType')
    bt = BallotType.objects.create(doc_type_id="draft",
                                   slug="irsg-approve",
                                   name="IRSG Approve",
                                   question="Is this draft ready for publication in the IRTF stream?",
                                  )
    bt.positions.set(['yes','noobj','recuse','notready','moretime'])

def reverse(apps, schema_editor):
    State = apps.get_model('doc','State')
    State.objects.filter(type_id__in=('draft-stream-irtf',), slug='irsg_review').delete()

    Position = apps.get_model('name','BallotPositionName')
    for pos in ("moretime", "notready"):
        Position.objects.filter(slug=pos).delete()

    IRSGBallot = apps.get_model('doc','BallotType')
    IRSGBallot.objects.filter(slug="irsg-approve").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0026_add_draft_rfceditor_state'),
        ('name', '0007_fix_m2m_slug_id_length'),
    ]

    operations = [
        migrations.RunPython(forward,reverse),
        migrations.RenameField(
            model_name='ballotpositiondocevent',
            old_name='ad',
            new_name='pos_by',
        ),

    ]
