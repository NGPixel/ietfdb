# Copyright The IETF Trust 2007, All Rights Reserved

from django.db import models
from ietf.idtracker.models import Acronym, PersonOrOrgInfo, IRTF, AreaGroup, Area, IETFWG
import datetime
#from ietf.utils import log

class IdSubmissionStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.CharField(blank=True, maxlength=255)
    def __str__(self):
	return "%s" % self.status_value
    class Meta:
        db_table = 'id_submission_status'
    class Admin:
	pass

class IdSubmissionDetail(models.Model):
    submission_id = models.AutoField(primary_key=True)
    #temp_id_document_tag = models.IntegerField(editable=False)	# obsolete
    status = models.ForeignKey(IdSubmissionStatus)
    last_updated_date = models.DateField()
    last_updated_time = models.CharField()
    id_document_name = models.CharField(blank=True, maxlength=255)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(maxlength=255)
    creation_date = models.DateField(default=datetime.date.today)
    submission_date = models.DateField(null=True, blank=True)
    remote_ip = models.CharField(blank=True, maxlength=100)
    revision = models.CharField(blank=True, maxlength=3)
    submitter = models.ForeignKey(PersonOrOrgInfo, db_column='submitter_tag', raw_id_admin=True)
    auth_key = models.CharField(blank=True, maxlength=255)
    idnits_message = models.TextField(blank=True)
    file_type = models.CharField(blank=True, maxlength=50)
    comment_to_sec = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    txt_page_count = models.IntegerField(null=True, blank=True)
    error_message = models.CharField(blank=True, maxlength=255)
    warning_message = models.TextField(blank=True)
    wg_submission = models.IntegerField(null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    man_posted_date = models.DateField(null=True, blank=True)
    man_posted_by = models.CharField(blank=True, maxlength=255)
    first_two_pages = models.TextField(blank=True)
    sub_email_priority = models.IntegerField(null=True, blank=True)
    invalid_version = models.IntegerField(null=True, blank=True)
    idnits_failed = models.IntegerField(null=True, blank=True)
    def save(self):
	self.last_updated_date = datetime.date.today()
	self.last_updated_time = datetime.datetime.now().time()
	super(IdSubmissionDetail, self).save()
    class Meta:
        db_table = 'id_submission_detail'

# No primary key.  django doesn't like that.  Ponder what to do about that.
class IdSubmissionEnv(models.Model):
    max_live = models.IntegerField(null=True, blank=True)
    staging_path = models.CharField(blank=True, maxlength=255)
    max_interval = models.IntegerField(null=True, blank=True)
    current_manual_proc_date = models.IntegerField(null=True, blank=True)
    init_rev_approved_msg = models.TextField(blank=True)
    submitter_auth_msg = models.TextField(blank=True)
    id_action_announcement = models.TextField(blank=True)
    target_path_web = models.CharField(blank=True, maxlength=255)
    target_path_ftp = models.CharField(blank=True, maxlength=255)
    side_bar_html = models.TextField(blank=True)
    staging_url = models.CharField(blank=True, maxlength=255)
    top_bar_html = models.TextField(blank=True)
    bottom_bar_html = models.TextField(blank=True)
    id_approval_request_msg = models.TextField(blank=True)
    emerg_auto_response = models.IntegerField(null=True, blank=True)
    max_same_draft_name = models.IntegerField(null=True, blank=True)
    max_same_draft_size = models.IntegerField(null=True, blank=True)
    max_same_submitter = models.IntegerField(null=True, blank=True)
    max_same_submitter_size = models.IntegerField(null=True, blank=True)
    max_same_wg_draft = models.IntegerField(null=True, blank=True)
    max_same_wg_draft_size = models.IntegerField(null=True, blank=True)
    max_daily_submission = models.IntegerField(null=True, blank=True)
    max_daily_submission_size = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'id_submission_env'

class IdApprovedDetail(models.Model):
    filename = models.CharField(blank=True, maxlength=255)
    approved_status = models.IntegerField(null=True, blank=True)
    approved_person = models.ForeignKey(PersonOrOrgInfo, db_column='approved_person_tag', raw_id_admin=True)
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.IntegerField(null=True, blank=True)
    def __str__(self):
	return "I-D %s pre-approval" % self.filename
    class Meta:
        db_table = 'id_approved_detail'
    class Admin:
	pass

class TempIdAuthors(models.Model):
    #id_document_tag = models.IntegerField(editable=False) 	# obsolete
    first_name = models.CharField(blank=True, maxlength=255)
    last_name = models.CharField(blank=True, maxlength=255)
    email_address = models.CharField(blank=True, maxlength=255)
    last_modified_date = models.DateField(null=True, blank=True)
    last_modified_time = models.CharField(blank=True, maxlength=100)
    author_order = models.IntegerField(default=0)
    submission = models.ForeignKey(IdSubmissionDetail)
    class Meta:
        db_table = 'temp_id_authors'
