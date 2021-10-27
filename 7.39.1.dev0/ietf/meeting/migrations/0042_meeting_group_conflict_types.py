# Generated by Django 2.2.20 on 2021-05-20 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('name', '0026_add_conflict_constraintnames'),
        ('meeting', '0041_assign_correct_constraintnames'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='group_conflict_types',
            field=models.ManyToManyField(blank=True, limit_choices_to={'is_group_conflict': True}, help_text='Types of scheduling conflict between groups to consider', to='name.ConstraintName'),
        ),
    ]
