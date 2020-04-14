# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.10 on 2018-02-20 10:52


from django.db import migrations, models
import django.db.models.deletion
import ietf.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('meeting', '0001_initial'),
        ('name', '0001_initial'),
        ('person', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AffiliationAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(help_text='Note that aliases will be matched case-insensitive and both before and after some clean-up.', max_length=255, unique=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'affiliation aliases',
            },
        ),
        migrations.CreateModel(
            name='AffiliationIgnoredEnding',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ending', models.CharField(help_text="Regexp with ending, e.g. 'Inc\\.?' - remember to escape .!", max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='CountryAlias',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alias', models.CharField(help_text="Note that lower-case aliases are matched case-insensitive while aliases with at least one uppercase letter is matched case-sensitive. So 'United States' is best entered as 'united states' so it both matches 'United States' and 'United states' and 'UNITED STATES', whereas 'US' is best entered as 'US' so it doesn't accidentally match an ordinary word like 'us'.", max_length=255)),
                ('country', ietf.utils.models.ForeignKey(max_length=255, on_delete=django.db.models.deletion.CASCADE, to='name.CountryName')),
            ],
            options={
                'verbose_name_plural': 'country aliases',
            },
        ),
        migrations.CreateModel(
            name='MeetingRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(max_length=255)),
                ('affiliation', models.CharField(blank=True, max_length=255)),
                ('country_code', models.CharField(max_length=2)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('meeting', ietf.utils.models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='meeting.Meeting')),
                ('person', ietf.utils.models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='person.Person')),
            ],
        ),
    ]
