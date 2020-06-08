# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-05-01 12:54
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify

robots = [
    ('Mail Archive', '/api/v2/person/person', 'secretariat', 'mailarchive@ietf.org'),
    ('Registration System', '/api/notify/meeting/registration', 'secretariat', 'registration@ietf.org'),
]

def forward(apps, schema_editor):
    RoleName = apps.get_model('name', 'RoleName')
    Role = apps.get_model('group', 'Role')
    Group =  apps.get_model('group', 'Group')
    User = apps.get_model('auth', 'User')
    Person = apps.get_model('person', 'Person')
    Email = apps.get_model('person', 'Email')
    PersonalApiKey = apps.get_model('person', 'PersonalApiKey')
    #
    rname, __ = RoleName.objects.get_or_create(slug='robot')
    # 
    for (name, endpoint, acronym, address) in robots:
        first_name, last_name = name.rsplit(None, 1)
        user, created  = User.objects.get_or_create(username=slugify(name))
        if created:
            user.first_name=first_name
            user.last_name=last_name
            user.is_staff=True
            user.is_active=True
            user.save()
        #
        person, created = Person.objects.get_or_create(name=name)
        if created:
            person.user = user
            person.ascii = name
            person.consent = True
            person.save()
        else:
            assert person.user == user
        #
        email, created = Email.objects.get_or_create(address=address)
        if created:
            email.origin = 'registration'
            email.person = person
            email.active = True
            email.save()
        else:
            assert email.person == person
        #
        group = Group.objects.get(acronym=acronym)
        role, created = Role.objects.get_or_create(person=person, name=rname, group=group, email=email)
        #
        key, created = PersonalApiKey.objects.get_or_create(person=person, endpoint=endpoint, valid=True)

def reverse(apps, schema_editor):
    Person = apps.get_model('person', 'Person')
    for (name, endpoint, acronym, address) in robots:
        deleted = Person.objects.filter(name=name).delete()
        print('deleted: %s' % deleted)

class Migration(migrations.Migration):

    dependencies = [
        ('group', '0027_programs_have_parents'),
        ('name', '0012_role_name_robots'),
    ]

    operations = [
        migrations.RunPython(forward, reverse),
    ]
