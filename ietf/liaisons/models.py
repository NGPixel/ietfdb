# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from django.utils.text import slugify

from ietf.person.models import Person
from ietf.name.models import (LiaisonStatementPurposeName, LiaisonStatementState,
                              LiaisonStatementEventTypeName, LiaisonStatementTagName,
                              DocRelationshipName)
from ietf.doc.models import Document
from ietf.person.models import Email
from ietf.group.models import Group


class LiaisonStatement(models.Model):
    title = models.CharField(blank=True, max_length=255)
    other_identifiers = models.TextField(blank=True, null=True) # Identifiers from other bodies
    purpose = models.ForeignKey(LiaisonStatementPurposeName)
    body = models.TextField(blank=True)
    deadline = models.DateField(null=True, blank=True)

    from_groups = models.ManyToManyField(Group, blank=True, related_name='liaisonsatement_from_set')
    from_name = models.CharField(max_length=255, help_text="Name of the sender body")

    to_groups = models.ManyToManyField(Group, blank=True, related_name='liaisonsatement_to_set') 
    to_name = models.CharField(max_length=255, help_text="Name of the recipient body")

    tags = models.ManyToManyField(LiaisonStatementTagName, blank=True, null=True)

    from_contact = models.ForeignKey(Email, blank=True, null=True)
    to_contacts = models.CharField(blank=True, max_length=255, help_text="Contacts at recipient body") 
    response_contacts = models.CharField(blank=True, max_length=255, help_text="Where to send a response") # RFC4053 
    technical_contacts = models.CharField(blank=True, max_length=255, help_text="Who to contact for clarification") # RFC4053
    action_holder_contacts = models.CharField(blank=True, max_length=255, help_text="Who makes sure action is completed")  # incoming only?
    cc_contacts = models.TextField(blank=True)

    attachments = models.ManyToManyField(Document, through='LiaisonStatementAttachments', blank=True)

    def name(self):
        if self.from_group:
            frm = self.from_group.acronym or self.from_group.name
        else:
            frm = self.from_name
        if self.to_group:
            to = self.to_group.acronym or self.to_group.name
        else:
            to = self.to_name
        return slugify("liaison" + " " + self.submitted.strftime("%Y-%m-%d") + " " + frm[:50] + " " + to[:50] + " " + self.title[:115])

    def __unicode__(self):
        return self.title or u"<no title>"


class LiaisonStatementAttachments(models.Model):
    statement = models.ForeignKey(LiaisonStatement)
    document = models.ForeignKey(Document)
    removed = models.BooleanField(default=False)


class RelatedLiaisonStatement(models.Model):
    source = models.ForeignKey(LiaisonStatement, related_name='source_of_set')
    target = models.ForeignKey(LiaisonStatement, related_name='target_of_set')
    relationship = models.ForeignKey(DocRelationshipName)


class LiaisonStatementGroupContacts(models.Model):
    group = models.ForeignKey(Group, unique=True) 
    default_reply_to = models.CharField(max_length=255)


class LiaisonStatementEvent(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    type = models.ForeignKey(LiaisonStatementEventTypeName)
    by = models.ForeignKey(Person)
    statement = models.ForeignKey(LiaisonStatement)
    desc = models.TextField()
