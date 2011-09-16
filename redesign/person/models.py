# Copyright The IETF Trust 2007, All Rights Reserved

import datetime

from django.db import models
from django.contrib.auth.models import User

from redesign.person.name import name_parts

class PersonInfo(models.Model):
    time = models.DateTimeField(default=datetime.datetime.now)      # When this Person record entered the system
    name = models.CharField(max_length=255, db_index=True) # The normal unicode form of the name.  This must be
                                                        # set to the same value as the ascii-form if equal.
    ascii = models.CharField(max_length=255)            # The normal ascii-form of the name.
    ascii_short = models.CharField(max_length=32, null=True, blank=True)      # The short ascii-form of the name.  Also in alias table if non-null
    address = models.TextField(max_length=255, blank=True)
    affiliation = models.CharField(max_length=255, blank=True)

    def __unicode__(self):
        return self.name
    def name_parts(self):
        return name_parts(self.name)
    def ascii_parts(self):
        return name_parts(self.ascii)
    def short(self):
        if self.ascii_short:
            return self.ascii_short
        else:
            prefix, first, middle, last, suffix = self.ascii_parts()
            return (first and first[0]+"." or "")+(middle or "")+" "+last+(suffix and " "+suffix or "")
    def role_email(self, role_name, group):
        e = Email.objects.filter(person=self, role__group=group, role__name=role_name)
        if e:
            return e[0]
        e = self.email_set.order_by("-active")
        if e:
            return e[0]
        return None
    def email_address(self):
        e = self.email_set.filter(active=True)
        if e:
            return e[0]
        else:
            return ""
    def formatted_email(self):
        e = self.email_set.order_by("-active")
        if e:
            return e[0].formatted_email()
        else:
            return ""
    def full_name_as_key(self):
        return self.name.lower().replace(" ", ".")
    class Meta:
        abstract = True

class Person(PersonInfo):
    user = models.OneToOneField(User, blank=True, null=True)
    
    def person(self): # little temporary wrapper to help porting to new schema
        return self
        
class PersonHistory(PersonInfo):
    person = models.ForeignKey(Person, related_name="history_set")
    user = models.ForeignKey(User, blank=True, null=True)
    
class Alias(models.Model):
    """This is used for alternative forms of a name.  This is the
    primary lookup point for names, and should always contain the
    unicode form (and ascii form, if different) of a name which is
    recorded in the Person record.
    """
    person = models.ForeignKey(Person)
    name = models.CharField(max_length=255, db_index=True)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "Aliases"

class Email(models.Model):
    address = models.CharField(max_length=64, primary_key=True)
    person = models.ForeignKey(Person, null=True)
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)      # Old email addresses are *not* purged, as history
                                        # information points to persons through these
    def __unicode__(self):
        return self.address

    def get_name(self):
        return self.person.name if self.person else self.address

    def formatted_email(self):
        if self.person and self.person.name:
            return u'"%s" <%s>' % (self.person.name, self.address)
        else:
            return self.address
            
