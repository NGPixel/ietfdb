# Generated by Django 2.2.14 on 2020-07-17 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0013_auto_20200711_1036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='personalapikey',
            name='endpoint',
            field=models.CharField(choices=[('/api/iesg/position', '/api/iesg/position'), ('/api/v2/person/person', '/api/v2/person/person'), ('/api/meeting/session/video/url', '/api/meeting/session/video/url'), ('/api/notify/meeting/registration', '/api/notify/meeting/registration')], max_length=128),
        ),
    ]
