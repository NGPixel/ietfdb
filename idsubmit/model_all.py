# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#     * Rearrange models' order
#     * Make sure each model has one field with primary_key=True
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.

from django.db import models

class Acronym(models.Model):
    acronym_id = models.IntegerField(primary_key=True)
    acronym = models.TextField(unique=True, blank=True)
    name = models.TextField(unique=True)
    name_key = models.TextField()
    class Meta:
        db_table = 'acronym'

class AgendaCat(models.Model):
    agenda_cat_id = models.IntegerField(primary_key=True)
    agenda_cat_value = models.CharField(blank=True, maxlength=300)
    class Meta:
        db_table = 'agenda_cat'

class AgendaItems(models.Model):
    agenda_item_id = models.IntegerField(primary_key=True)
    telechat_id = models.IntegerField()
    agenda_cat_id = models.IntegerField(null=True, blank=True)
    ballot_id = models.IntegerField()
    group_acronym_id = models.IntegerField()
    agenda_item_status_id = models.IntegerField(null=True, blank=True)
    iana_note = models.TextField(blank=True)
    other_note = models.TextField(blank=True)
    agenda_note_cat_id = models.IntegerField(null=True, blank=True)
    note_draft_by = models.IntegerField(null=True, blank=True)
    item_num = models.IntegerField(null=True, blank=True)
    total_num = models.IntegerField(null=True, blank=True)
    agenda_item_gr_status_id = models.IntegerField(null=True, blank=True)
    wg_action_status = models.IntegerField(null=True, blank=True)
    wg_action_status_sub = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'agenda_items'

class AllId(models.Model):
    id_document_tag = models.IntegerField(primary_key=True)
    filename = models.CharField(blank=True, maxlength=300)
    last_active_revision = models.TextField(blank=True)
    class Meta:
        db_table = 'all_id'

class AnnouncedFrom(models.Model):
    announced_from_id = models.IntegerField(primary_key=True)
    announced_from_value = models.CharField(blank=True, maxlength=765)
    announced_from_email = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'announced_from'

class AnnouncedTo(models.Model):
    announced_to_id = models.IntegerField(primary_key=True)
    announced_to_value = models.CharField(blank=True, maxlength=765)
    announced_to_email = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'announced_to'

class Announcements(models.Model):
    announcement_id = models.IntegerField(primary_key=True)
    announced_by = models.IntegerField()
    announced_date = models.DateField(null=True, blank=True)
    announced_time = models.CharField(blank=True, maxlength=60)
    announcement_text = models.TextField(blank=True)
    announced_from_id = models.IntegerField(null=True, blank=True)
    cc = models.CharField(blank=True, maxlength=765)
    subject = models.CharField(blank=True, maxlength=765)
    extra = models.TextField(blank=True)
    announced_to_id = models.IntegerField(null=True, blank=True)
    nomcom = models.IntegerField(null=True, blank=True)
    nomcom_chair_id = models.IntegerField(null=True, blank=True)
    manualy_added = models.IntegerField(null=True, blank=True)
    other_val = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'announcements'

class AreaDirectors(models.Model):
    id = models.IntegerField(primary_key=True)
    area_acronym_id = models.IntegerField(unique=True, null=True, blank=True)
    person_or_org_tag = models.IntegerField(unique=True)
    class Meta:
        db_table = 'area_directors'

class AreaGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    area_acronym_id = models.IntegerField(unique=True)
    group_acronym_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'area_group'

class AreaStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'area_status'

class Areas(models.Model):
    area_acronym_id = models.IntegerField(primary_key=True)
    start_date = models.DateField()
    concluded_date = models.DateField(null=True, blank=True)
    status_id = models.IntegerField()
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField()
    extra_email_addresses = models.TextField(blank=True)
    class Meta:
        db_table = 'areas'

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, maxlength=240)
    class Meta:
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_group_permissions'

class AuthMessage(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    message = models.TextField()
    class Meta:
        db_table = 'auth_message'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=150)
    content_type_id = models.IntegerField()
    codename = models.CharField(unique=True, maxlength=300)
    class Meta:
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.CharField(unique=True, maxlength=90)
    first_name = models.CharField(maxlength=90)
    last_name = models.CharField(maxlength=90)
    email = models.CharField(maxlength=225)
    password = models.CharField(maxlength=384)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    is_superuser = models.IntegerField()
    last_login = models.DateTimeField()
    date_joined = models.DateTimeField()
    class Meta:
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    group_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    permission_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'auth_user_user_permissions'

class BallotInfo(models.Model):
    ballot_id = models.IntegerField(primary_key=True)
    active = models.IntegerField()
    an_sent = models.IntegerField()
    an_sent_date = models.DateField(null=True, blank=True)
    an_sent_by = models.IntegerField(null=True, blank=True)
    defer = models.IntegerField(null=True, blank=True)
    defer_by = models.IntegerField(null=True, blank=True)
    defer_date = models.DateField(null=True, blank=True)
    approval_text = models.TextField(blank=True)
    last_call_text = models.TextField(blank=True)
    ballot_writeup = models.TextField(blank=True)
    ballot_issued = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ballot_info'

class Ballots(models.Model):
    id = models.IntegerField(primary_key=True)
    ballot_id = models.IntegerField(unique=True)
    ad_id = models.IntegerField(unique=True)
    yes_col = models.IntegerField()
    no_col = models.IntegerField()
    abstain = models.IntegerField()
    approve = models.IntegerField()
    discuss = models.IntegerField()
    recuse = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ballots'

class BallotsComment(models.Model):
    id = models.IntegerField(primary_key=True)
    ballot_id = models.IntegerField(unique=True)
    ad_id = models.IntegerField(unique=True)
    comment_date = models.DateField()
    revision = models.TextField()
    active = models.IntegerField()
    comment_text = models.TextField(blank=True)
    class Meta:
        db_table = 'ballots_comment'

class BallotsDiscuss(models.Model):
    id = models.IntegerField(primary_key=True)
    ballot_id = models.IntegerField(unique=True)
    ad_id = models.IntegerField(unique=True)
    discuss_date = models.DateField()
    revision = models.TextField()
    active = models.IntegerField()
    discuss_text = models.TextField(blank=True)
    class Meta:
        db_table = 'ballots_discuss'

class BashAgenda(models.Model):
    telechat_id = models.IntegerField(primary_key=True)
    bash_agenda_txt = models.TextField(blank=True)
    change_agenda = models.IntegerField(null=True, blank=True)
    change_agenda_note = models.TextField(blank=True)
    class Meta:
        db_table = 'bash_agenda'

class Chairs(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField()
    chair_name = models.CharField(blank=True, maxlength=75)
    class Meta:
        db_table = 'chairs'

class ChairsHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    chair_type_id = models.IntegerField(null=True, blank=True)
    present_chair = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'chairs_history'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user_id = models.IntegerField()
    content_type_id = models.IntegerField(null=True, blank=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(maxlength=600)
    action_flag = models.IntegerField()
    change_message = models.TextField()
    class Meta:
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(maxlength=300)
    app_label = models.CharField(unique=True, maxlength=300)
    model = models.CharField(unique=True, maxlength=300)
    class Meta:
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, maxlength=120)
    session_data = models.TextField()
    expire_date = models.DateTimeField()
    class Meta:
        db_table = 'django_session'

class DjangoSite(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(maxlength=300)
    name = models.CharField(maxlength=150)
    class Meta:
        db_table = 'django_site'

class DocumentComments(models.Model):
    id = models.IntegerField(primary_key=True)
    document_id = models.IntegerField()
    rfc_flag = models.IntegerField(null=True, blank=True)
    public_flag = models.IntegerField(null=True, blank=True)
    comment_date = models.DateField()
    comment_time = models.CharField(maxlength=60)
    version = models.TextField(blank=True)
    comment_text = models.TextField(blank=True)
    created_by = models.IntegerField(null=True, blank=True)
    result_state = models.IntegerField(null=True, blank=True)
    origin_state = models.IntegerField(null=True, blank=True)
    ballot = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'document_comments'

class DtRequest(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.CharField(maxlength=765)
    request_by = models.IntegerField()
    request_date = models.DateField(null=True, blank=True)
    cur_version = models.CharField(blank=True, maxlength=15)
    status = models.TextField(blank=True)
    done_flag = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'dt_request'

class EmailAddresses(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField()
    email_type = models.CharField(maxlength=12)
    email_priority = models.IntegerField()
    email_address = models.CharField(blank=True, maxlength=765)
    email_comment = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'email_addresses'

class FromBodies(models.Model):
    from_id = models.IntegerField(primary_key=True)
    body_name = models.CharField(blank=True, maxlength=105)
    poc = models.IntegerField(null=True, blank=True)
    is_liaison_manager = models.IntegerField(null=True, blank=True)
    other_sdo = models.IntegerField(null=True, blank=True)
    email_priority = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'from_bodies'

class GChairs(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(unique=True)
    group_acronym_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'g_chairs'

class GEditors(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(unique=True)
    person_or_org_tag = models.IntegerField(unique=True)
    class Meta:
        db_table = 'g_editors'

class GSecretaries(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'g_secretaries'

class GSecretary(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField()
    person_or_org_tag = models.IntegerField()
    class Meta:
        db_table = 'g_secretary'

class GStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'g_status'

class GTechAdvisors(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(unique=True)
    person_or_org_tag = models.IntegerField(unique=True)
    class Meta:
        db_table = 'g_tech_advisors'

class GType(models.Model):
    group_type_id = models.IntegerField(primary_key=True)
    group_type = models.TextField()
    class Meta:
        db_table = 'g_type'

class GeneralInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    info_name = models.CharField(blank=True, maxlength=150)
    info_text = models.TextField(blank=True)
    info_header = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'general_info'

class GoalsMilestones(models.Model):
    gm_id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField()
    description = models.TextField(blank=True)
    expected_due_date = models.DateField(null=True, blank=True)
    done_date = models.DateField(null=True, blank=True)
    done = models.CharField(blank=True, maxlength=12)
    last_modified_date = models.DateField()
    class Meta:
        db_table = 'goals_milestones'

class GroupFlag(models.Model):
    group_flag = models.IntegerField(primary_key=True)
    group_flag_val = models.TextField(blank=True)
    equiv_doc_state_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'group_flag'

class GroupInternal(models.Model):
    group_acronym_id = models.IntegerField(unique=True)
    note = models.TextField(blank=True)
    status_date = models.DateField(null=True, blank=True)
    agenda = models.IntegerField(null=True, blank=True)
    token_name = models.CharField(blank=True, maxlength=75)
    pwg_cat_id = models.IntegerField(null=True, blank=True)
    telechat_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'group_internal'

class GroupsIetf(models.Model):
    group_acronym_id = models.IntegerField(primary_key=True)
    group_type_id = models.IntegerField()
    proposed_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    dormant_date = models.DateField(null=True, blank=True)
    concluded_date = models.DateField(null=True, blank=True)
    status_id = models.IntegerField()
    area_director_id = models.IntegerField(null=True, blank=True)
    meeting_scheduled = models.TextField(blank=True)
    email_address = models.CharField(blank=True, maxlength=180)
    email_subscribe = models.CharField(blank=True, maxlength=360)
    email_keyword = models.CharField(blank=True, maxlength=150)
    email_archive = models.CharField(blank=True, maxlength=285)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField()
    meeting_scheduled_old = models.TextField(blank=True)
    class Meta:
        db_table = 'groups_ietf'

class HitCounter(models.Model):
    id = models.IntegerField(primary_key=True)
    page_name = models.CharField(blank=True, maxlength=765)
    hit_count = models.IntegerField(null=True, blank=True)
    last_visitor = models.CharField(blank=True, maxlength=765)
    last_visited_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'hit_counter'

class IdApprovedDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    filename = models.CharField(blank=True, maxlength=765)
    approved_status = models.IntegerField(null=True, blank=True)
    approved_person_tag = models.IntegerField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    recorded_by = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'id_approved_detail'

class IdAuthors(models.Model):
    id = models.IntegerField(primary_key=True)
    id_document_tag = models.IntegerField(unique=True)
    person_or_org_tag = models.IntegerField(unique=True)
    author_order = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'id_authors'

class IdDates(models.Model):
    id = models.IntegerField(primary_key=True)
    id_date = models.DateField(null=True, blank=True)
    date_name = models.CharField(blank=True, maxlength=765)
    f_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'id_dates'

class IdIntendedStatus(models.Model):
    intended_status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'id_intended_status'

class IdInternal(models.Model):
    id_document_tag = models.IntegerField(unique=True)
    rfc_flag = models.IntegerField(null=True, blank=True)
    ballot_id = models.IntegerField()
    primary_flag = models.IntegerField(null=True, blank=True)
    group_flag = models.IntegerField()
    token_name = models.CharField(blank=True, maxlength=75)
    token_email = models.CharField(blank=True, maxlength=765)
    note = models.TextField(blank=True)
    status_date = models.DateField(null=True, blank=True)
    email_display = models.CharField(blank=True, maxlength=150)
    agenda = models.IntegerField(null=True, blank=True)
    cur_state = models.IntegerField()
    prev_state = models.IntegerField()
    assigned_to = models.CharField(blank=True, maxlength=75)
    mark_by = models.IntegerField()
    job_owner = models.IntegerField()
    event_date = models.DateField(null=True, blank=True)
    area_acronym_id = models.IntegerField()
    cur_sub_state_id = models.IntegerField(null=True, blank=True)
    prev_sub_state_id = models.IntegerField(null=True, blank=True)
    returning_item = models.IntegerField(null=True, blank=True)
    telechat_date = models.DateField(null=True, blank=True)
    via_rfc_editor = models.IntegerField(null=True, blank=True)
    state_change_notice_to = models.CharField(blank=True, maxlength=765)
    dnp = models.IntegerField(null=True, blank=True)
    dnp_date = models.DateField(null=True, blank=True)
    noproblem = models.IntegerField(null=True, blank=True)
    resurrect_requested_by = models.IntegerField(null=True, blank=True)
    approved_in_minute = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'id_internal'

class IdRestrictedWord(models.Model):
    id = models.IntegerField(primary_key=True)
    restricted_word = models.TextField()
    class Meta:
        db_table = 'id_restricted_word'

class IdStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'id_status'

class IdSubmissionDetail(models.Model):
    submission_id = models.IntegerField(primary_key=True)
    temp_id_document_tag = models.IntegerField(null=True, blank=True)
    status_id = models.IntegerField(null=True, blank=True)
    last_updated_date = models.DateField(null=True, blank=True)
    last_updated_time = models.CharField(blank=True, maxlength=75)
    id_document_name = models.CharField(blank=True, maxlength=765)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(blank=True, maxlength=765)
    creation_date = models.DateField(null=True, blank=True)
    submission_date = models.DateField(null=True, blank=True)
    remote_ip = models.CharField(blank=True, maxlength=300)
    revision = models.TextField(blank=True)
    submitter_tag = models.IntegerField(null=True, blank=True)
    auth_key = models.CharField(blank=True, maxlength=765)
    idnits_message = models.TextField(blank=True)
    file_type = models.CharField(blank=True, maxlength=150)
    comment_to_sec = models.TextField(blank=True)
    abstract = models.TextField(blank=True)
    txt_page_count = models.IntegerField(null=True, blank=True)
    error_message = models.CharField(blank=True, maxlength=765)
    warning_message = models.TextField(blank=True)
    wg_submission = models.IntegerField(null=True, blank=True)
    filesize = models.IntegerField(null=True, blank=True)
    man_posted_date = models.DateField(null=True, blank=True)
    man_posted_by = models.CharField(blank=True, maxlength=765)
    first_two_pages = models.TextField(blank=True)
    sub_email_priority = models.IntegerField(null=True, blank=True)
    invalid_version = models.IntegerField(null=True, blank=True)
    idnits_failed = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'id_submission_detail'

class IdSubmissionEnv(models.Model):
    max_live = models.IntegerField(null=True, blank=True)
    staging_path = models.CharField(blank=True, maxlength=765)
    max_interval = models.IntegerField(null=True, blank=True)
    current_manual_proc_date = models.IntegerField(null=True, blank=True)
    init_rev_approved_msg = models.TextField(blank=True)
    submitter_auth_msg = models.TextField(blank=True)
    id_action_announcement = models.TextField(blank=True)
    target_path_web = models.CharField(blank=True, maxlength=765)
    target_path_ftp = models.CharField(blank=True, maxlength=765)
    side_bar_html = models.TextField(blank=True)
    staging_url = models.CharField(blank=True, maxlength=765)
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

class IdSubmissionStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'id_submission_status'

class IdstUsers(models.Model):
    id = models.IntegerField(primary_key=True)
    login_name = models.CharField(maxlength=765)
    password = models.CharField(blank=True, maxlength=765)
    random_str = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'idst_users'

class IesgHistory(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField()
    area_acronym_id = models.IntegerField()
    person_or_org_tag = models.IntegerField()
    class Meta:
        db_table = 'iesg_history'

class IesgLogin(models.Model):
    id = models.IntegerField(primary_key=True)
    login_name = models.CharField(blank=True, maxlength=765)
    password = models.CharField(maxlength=75)
    user_level = models.IntegerField()
    first_name = models.CharField(blank=True, maxlength=75)
    last_name = models.CharField(blank=True, maxlength=75)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    pgp_id = models.CharField(blank=True, maxlength=60)
    default_search = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'iesg_login'

class IesgPassword(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    login_name = models.CharField(blank=True, maxlength=765)
    password = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'iesg_password'

class IetfauthUsermap(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField(unique=True)
    person_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'ietfauth_usermap'

class ImportedMailingList(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    list_acronym = models.CharField(blank=True, maxlength=765)
    list_name = models.CharField(blank=True, maxlength=765)
    list_domain = models.CharField(blank=True, maxlength=75)
    class Meta:
        db_table = 'imported_mailing_list'

class InterimInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    meeting_date = models.CharField(blank=True, maxlength=765)
    message_body = models.TextField(blank=True)
    class Meta:
        db_table = 'interim_info'

class InternetDrafts(models.Model):
    id_document_tag = models.IntegerField(primary_key=True)
    id_document_name = models.CharField(blank=True, maxlength=765)
    id_document_key = models.CharField(blank=True, maxlength=765)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(blank=True, maxlength=765)
    revision = models.TextField()
    revision_date = models.DateField(null=True, blank=True)
    file_type = models.CharField(blank=True, maxlength=60)
    txt_page_count = models.IntegerField(null=True, blank=True)
    local_path = models.CharField(blank=True, maxlength=765)
    start_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=True, blank=True)
    abstract = models.TextField(blank=True)
    dunn_sent_date = models.DateField(null=True, blank=True)
    extension_date = models.DateField(null=True, blank=True)
    status_id = models.IntegerField()
    intended_status_id = models.IntegerField()
    lc_sent_date = models.DateField(null=True, blank=True)
    lc_changes = models.TextField(blank=True)
    lc_expiration_date = models.DateField(null=True, blank=True)
    b_sent_date = models.DateField(null=True, blank=True)
    b_discussion_date = models.DateField(null=True, blank=True)
    b_approve_date = models.DateField(null=True, blank=True)
    wgreturn_date = models.DateField(null=True, blank=True)
    rfc_number = models.IntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField()
    replaced_by = models.IntegerField(null=True, blank=True)
    review_by_rfc_editor = models.IntegerField(null=True, blank=True)
    expired_tombstone = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'internet_drafts'

class IprContacts(models.Model):
    contact_id = models.IntegerField(primary_key=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    contact_type = models.IntegerField(null=True, blank=True)
    name = models.CharField(blank=True, maxlength=765)
    title = models.CharField(blank=True, maxlength=765)
    department = models.CharField(blank=True, maxlength=765)
    telephone = models.CharField(blank=True, maxlength=75)
    fax = models.CharField(blank=True, maxlength=75)
    email = models.CharField(blank=True, maxlength=765)
    address1 = models.CharField(blank=True, maxlength=765)
    address2 = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'ipr_contacts'

class IprDetail(models.Model):
    ipr_id = models.IntegerField(primary_key=True)
    p_h_legal_name = models.CharField(blank=True, maxlength=765)
    document_title = models.CharField(blank=True, maxlength=765)
    rfc_number = models.IntegerField(null=True, blank=True)
    id_document_tag = models.IntegerField(null=True, blank=True)
    other_designations = models.CharField(blank=True, maxlength=765)
    p_applications = models.CharField(blank=True, maxlength=765)
    date_applied = models.CharField(blank=True, maxlength=765)
    selecttype = models.TextField(blank=True)
    disclouser_identify = models.CharField(blank=True, maxlength=765)
    licensing_option = models.IntegerField(null=True, blank=True)
    other_notes = models.TextField(blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    status = models.IntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    old_ipr_url = models.CharField(blank=True, maxlength=765)
    additional_old_title1 = models.CharField(blank=True, maxlength=765)
    additional_old_url1 = models.CharField(blank=True, maxlength=765)
    additional_old_title2 = models.CharField(blank=True, maxlength=765)
    additional_old_url2 = models.CharField(blank=True, maxlength=765)
    country = models.CharField(blank=True, maxlength=300)
    p_notes = models.TextField(blank=True)
    third_party = models.IntegerField(null=True, blank=True)
    lic_opt_a_sub = models.IntegerField(null=True, blank=True)
    lic_opt_b_sub = models.IntegerField(null=True, blank=True)
    lic_opt_c_sub = models.IntegerField(null=True, blank=True)
    generic = models.IntegerField(null=True, blank=True)
    selectowned = models.TextField(blank=True)
    comply = models.IntegerField(null=True, blank=True)
    lic_checkbox = models.IntegerField(null=True, blank=True)
    update_notified_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'ipr_detail'

class IprIds(models.Model):
    id = models.IntegerField(primary_key=True)
    id_document_tag = models.IntegerField(null=True, blank=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    revision = models.TextField(blank=True)
    class Meta:
        db_table = 'ipr_ids'

class IprLicensing(models.Model):
    licensing_option = models.IntegerField(primary_key=True)
    licensing_option_value = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'ipr_licensing'

class IprNotifications(models.Model):
    id = models.IntegerField(primary_key=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    notification = models.TextField(blank=True)
    date_sent = models.DateField(null=True, blank=True)
    time_sent = models.CharField(blank=True, maxlength=75)
    class Meta:
        db_table = 'ipr_notifications'

class IprRfcs(models.Model):
    id = models.IntegerField(primary_key=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    rfc_number = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ipr_rfcs'

class IprSelecttype(models.Model):
    type_id = models.IntegerField(primary_key=True)
    selecttype = models.IntegerField(null=True, blank=True)
    type_display = models.CharField(blank=True, maxlength=45)
    class Meta:
        db_table = 'ipr_selecttype'

class IprUpdates(models.Model):
    id = models.IntegerField(primary_key=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    updated = models.IntegerField(null=True, blank=True)
    status_to_be = models.IntegerField(null=True, blank=True)
    processed = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'ipr_updates'

class Irtf(models.Model):
    irtf_id = models.IntegerField(primary_key=True)
    irtf_acronym = models.CharField(blank=True, maxlength=75)
    irtf_name = models.CharField(blank=True, maxlength=765)
    charter_text = models.TextField(blank=True)
    meeting_scheduled = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'irtf'

class IrtfChairs(models.Model):
    id = models.IntegerField(primary_key=True)
    irtf_id = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'irtf_chairs'

class LiaisonDetail(models.Model):
    detail_id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(null=True, blank=True)
    from_id = models.IntegerField(null=True, blank=True)
    to_body = models.CharField(blank=True, maxlength=765)
    title = models.CharField(blank=True, maxlength=765)
    response_contact = models.CharField(blank=True, maxlength=765)
    technical_contact = models.CharField(blank=True, maxlength=765)
    purpose = models.TextField(blank=True)
    body = models.TextField(blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    cc1 = models.TextField(blank=True)
    cc2 = models.CharField(blank=True, maxlength=150)
    submitter_name = models.CharField(blank=True, maxlength=765)
    submitter_email = models.CharField(blank=True, maxlength=765)
    by_secretariat = models.IntegerField(null=True, blank=True)
    to_poc = models.CharField(blank=True, maxlength=765)
    to_email = models.CharField(blank=True, maxlength=765)
    purpose_id = models.IntegerField(null=True, blank=True)
    replyto = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'liaison_detail'

class LiaisonDetailTemp(models.Model):
    detail_id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    submitted_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(null=True, blank=True)
    from_id = models.IntegerField(null=True, blank=True)
    to_body = models.CharField(blank=True, maxlength=765)
    title = models.CharField(blank=True, maxlength=765)
    response_contact = models.CharField(blank=True, maxlength=765)
    technical_contact = models.CharField(blank=True, maxlength=765)
    purpose = models.TextField(blank=True)
    body = models.TextField(blank=True)
    deadline_date = models.DateField(null=True, blank=True)
    cc1 = models.TextField(blank=True)
    cc2 = models.CharField(blank=True, maxlength=150)
    to_poc = models.CharField(blank=True, maxlength=765)
    to_email = models.CharField(blank=True, maxlength=765)
    purpose_id = models.IntegerField(null=True, blank=True)
    replyto = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'liaison_detail_temp'

class LiaisonManagers(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    email_priority = models.IntegerField(null=True, blank=True)
    sdo_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'liaison_managers'

class LiaisonPurpose(models.Model):
    purpose_id = models.IntegerField(primary_key=True)
    purpose_text = models.CharField(blank=True, maxlength=150)
    class Meta:
        db_table = 'liaison_purpose'

class LiaisonsInterim(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(blank=True, maxlength=765)
    submitter_name = models.CharField(blank=True, maxlength=765)
    submitter_email = models.CharField(blank=True, maxlength=765)
    submitted_date = models.DateField(null=True, blank=True)
    from_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'liaisons_interim'

class LiaisonsLiaisonDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    submitted_date = models.DateField()
    title = models.CharField(maxlength=765)
    class Meta:
        db_table = 'liaisons_liaison_detail'

class LiaisonsMembers(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    affiliation = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'liaisons_members'

class LiaisonsPersonOrOrgInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(maxlength=765)
    last_name = models.CharField(maxlength=765)
    class Meta:
        db_table = 'liaisons_person_or_org_info'

class LiaisonsUploads(models.Model):
    id = models.IntegerField(primary_key=True)
    file_title = models.CharField(maxlength=765)
    liaison_detail_id = models.IntegerField()
    file_extension = models.CharField(maxlength=30)
    class Meta:
        db_table = 'liaisons_uploads'

class MailingList(models.Model):
    mailing_list_id = models.CharField(primary_key=True, maxlength=75)
    request_date = models.DateField(null=True, blank=True)
    mlist_name = models.CharField(blank=True, maxlength=750)
    short_desc = models.CharField(blank=True, maxlength=750)
    long_desc = models.TextField(blank=True)
    requestor = models.CharField(blank=True, maxlength=750)
    requestor_email = models.CharField(blank=True, maxlength=750)
    admins = models.CharField(blank=True, maxlength=750)
    archive_remote = models.TextField(blank=True)
    archive_private = models.IntegerField(null=True, blank=True)
    initial = models.TextField(blank=True)
    welcome_message = models.TextField(blank=True)
    subscription = models.IntegerField(null=True, blank=True)
    post_who = models.IntegerField(null=True, blank=True)
    post_admin = models.IntegerField(null=True, blank=True)
    add_comment = models.TextField(blank=True)
    mail_type = models.IntegerField(null=True, blank=True)
    mail_cat = models.IntegerField(null=True, blank=True)
    auth_person_or_org_tag = models.IntegerField(null=True, blank=True)
    welcome_new = models.TextField(blank=True)
    approved = models.IntegerField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    reason_to_delete = models.TextField(blank=True)
    domain_name = models.CharField(blank=True, maxlength=30)
    class Meta:
        db_table = 'mailing_list'

class MailinglistsDomain(models.Model):
    id = models.IntegerField(primary_key=True)
    domain = models.CharField(maxlength=300)
    class Meta:
        db_table = 'mailinglists_domain'

class MailinglistsDomainApprovers(models.Model):
    id = models.IntegerField(primary_key=True)
    domain_id = models.IntegerField(unique=True)
    role_id = models.IntegerField(unique=True)
    class Meta:
        db_table = 'mailinglists_domain_approvers'

class ManagementIssues(models.Model):
    id = models.IntegerField(primary_key=True)
    telechat_id = models.IntegerField(null=True, blank=True)
    title = models.CharField(blank=True, maxlength=765)
    issue = models.TextField(blank=True)
    discussed_status_id = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    class Meta:
        db_table = 'management_issues'

class MeetingAgendaCount(models.Model):
    hit_count = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'meeting_agenda_count'

class MeetingAttendees(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(blank=True, maxlength=765)
    last_name = models.CharField(blank=True, maxlength=765)
    affiliated_company = models.CharField(blank=True, maxlength=765)
    email_address = models.CharField(blank=True, maxlength=765)
    meeting_num = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'meeting_attendees'

class MeetingHours(models.Model):
    hour_id = models.IntegerField(primary_key=True)
    hour_desc = models.CharField(blank=True, maxlength=60)
    class Meta:
        db_table = 'meeting_hours'

class MeetingRooms(models.Model):
    room_id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    room_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'meeting_rooms'

class MeetingTimes(models.Model):
    time_id = models.IntegerField(primary_key=True)
    time_desc = models.CharField(blank=True, maxlength=300)
    meeting_num = models.IntegerField(null=True, blank=True)
    day_id = models.IntegerField(null=True, blank=True)
    session_name_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'meeting_times'

class MeetingVenues(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    break_area_name = models.CharField(blank=True, maxlength=765)
    reg_area_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'meeting_venues'

class Meetings(models.Model):
    meeting_num = models.IntegerField(primary_key=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    city = models.CharField(blank=True, maxlength=765)
    state = models.CharField(blank=True, maxlength=765)
    country = models.CharField(blank=True, maxlength=765)
    ack = models.TextField(blank=True)
    agenda_html = models.TextField(blank=True)
    agenda_text = models.TextField(blank=True)
    future_meeting = models.TextField(blank=True)
    overview1 = models.TextField(blank=True)
    overview2 = models.TextField(blank=True)
    class Meta:
        db_table = 'meetings'

class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    message_name = models.CharField(maxlength=75)
    message_content = models.TextField()
    recipient = models.CharField(maxlength=300)
    class Meta:
        db_table = 'messages'

class MigrateStat(models.Model):
    id = models.IntegerField(primary_key=True)
    new_script = models.TextField()
    old_script = models.TextField(blank=True)
    need_done = models.TextField(blank=True)
    how_to_test = models.TextField(blank=True)
    status = models.TextField(blank=True)
    done_flag = models.IntegerField(null=True, blank=True)
    group_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'migrate_stat'

class Minutes(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(blank=True, maxlength=765)
    irtf = models.IntegerField(null=True, blank=True)
    interim = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'minutes'

class Nomcom(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    class Meta:
        db_table = 'nomcom'

class NomcomMembers(models.Model):
    chair_id = models.IntegerField(primary_key=True)
    voting_members = models.TextField(blank=True)
    non_voting_members = models.TextField(blank=True)
    class Meta:
        db_table = 'nomcom_members'

class NonSession(models.Model):
    non_session_id = models.IntegerField(primary_key=True)
    day_id = models.IntegerField(null=True, blank=True)
    non_session_ref_id = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    time_desc = models.CharField(blank=True, maxlength=225)
    class Meta:
        db_table = 'non_session'

class NonSessionRef(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'non_session_ref'

class NoneWgMailingList(models.Model):
    id = models.CharField(primary_key=True, maxlength=105)
    purpose = models.TextField(blank=True)
    area_acronym_id = models.IntegerField(null=True, blank=True)
    admin = models.TextField(blank=True)
    list_url = models.CharField(maxlength=765)
    s_name = models.CharField(blank=True, maxlength=765)
    s_email = models.CharField(blank=True, maxlength=765)
    status = models.IntegerField(null=True, blank=True)
    list_name = models.CharField(blank=True, maxlength=765)
    subscribe_url = models.CharField(blank=True, maxlength=765)
    subscribe_other = models.TextField(blank=True)
    ds_name = models.CharField(blank=True, maxlength=765)
    ds_email = models.CharField(blank=True, maxlength=765)
    msg_to_ad = models.TextField(blank=True)
    class Meta:
        db_table = 'none_wg_mailing_list'

class NotMeetingGroups(models.Model):
    group_acronym_id = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'not_meeting_groups'

class OldDocumentComments(models.Model):
    id = models.IntegerField(primary_key=True)
    comment_text = models.TextField(blank=True)
    class Meta:
        db_table = 'old_document_comments'

class OutstandingTasks(models.Model):
    id = models.IntegerField(primary_key=True)
    item_txt = models.CharField(blank=True, maxlength=765)
    task_status_id = models.IntegerField(null=True, blank=True)
    last_updated_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'outstanding_tasks'

class PersonOrOrgInfo(models.Model):
    person_or_org_tag = models.IntegerField(unique=True)
    record_type = models.TextField(blank=True)
    name_prefix = models.TextField(blank=True)
    first_name = models.TextField(blank=True)
    first_name_key = models.TextField(blank=True)
    middle_initial = models.TextField(blank=True)
    middle_initial_key = models.TextField(blank=True)
    last_name = models.TextField(blank=True)
    last_name_key = models.TextField(blank=True)
    name_suffix = models.TextField(blank=True)
    date_modified = models.DateField(null=True, blank=True)
    modified_by = models.TextField(blank=True)
    date_created = models.DateField(null=True, blank=True)
    created_by = models.TextField(blank=True)
    address_type = models.TextField(blank=True)
    class Meta:
        db_table = 'person_or_org_info'

class PhoneNumbers(models.Model):
    id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField()
    phone_type = models.TextField()
    phone_priority = models.IntegerField()
    phone_number = models.CharField(blank=True, maxlength=765)
    phone_comment = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'phone_numbers'

class PostalAddresses(models.Model):
    id = models.IntegerField(primary_key=True)
    address_type = models.TextField()
    address_priority = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField()
    person_title = models.TextField(blank=True)
    affiliated_company = models.TextField(blank=True)
    aff_company_key = models.TextField(blank=True)
    department = models.TextField(blank=True)
    staddr1 = models.TextField(blank=True)
    staddr2 = models.TextField(blank=True)
    mail_stop = models.TextField(blank=True)
    city = models.TextField(blank=True)
    state_or_prov = models.TextField(blank=True)
    postal_code = models.TextField(blank=True)
    country = models.TextField(blank=True)
    class Meta:
        db_table = 'postal_addresses'

class PrintName(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    firstname = models.TextField(blank=True)
    lastname = models.TextField()
    class Meta:
        db_table = 'print_name'

class PriorAddress(models.Model):
    person_or_org_tag = models.IntegerField(unique=True)
    address_type = models.TextField(blank=True)
    class Meta:
        db_table = 'prior_address'

class Proceedings(models.Model):
    meeting_num = models.IntegerField(primary_key=True)
    dir_name = models.CharField(blank=True, maxlength=75)
    sub_begin_date = models.DateField(null=True, blank=True)
    sub_cut_off_date = models.DateField(null=True, blank=True)
    frozen = models.IntegerField(null=True, blank=True)
    c_sub_cut_off_date = models.DateField(null=True, blank=True)
    pr_from_date = models.DateField(null=True, blank=True)
    pr_to_date = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'proceedings'

class PwgCat(models.Model):
    id = models.IntegerField(primary_key=True)
    pwg_status_val = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'pwg_cat'

class RedirectsCommand(models.Model):
    id = models.IntegerField(primary_key=True)
    command = models.CharField(unique=True, maxlength=150)
    url = models.CharField(maxlength=150)
    script_id = models.IntegerField()
    suffix_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'redirects_command'

class RedirectsRedirect(models.Model):
    id = models.IntegerField(primary_key=True)
    cgi = models.CharField(unique=True, maxlength=150)
    url = models.CharField(maxlength=765)
    rest = models.CharField(maxlength=300)
    remove = models.CharField(maxlength=150)
    class Meta:
        db_table = 'redirects_redirect'

class RedirectsSuffix(models.Model):
    id = models.IntegerField(primary_key=True)
    rest = models.CharField(maxlength=300)
    remove = models.CharField(maxlength=150)
    class Meta:
        db_table = 'redirects_suffix'

class RefDocStatesNew(models.Model):
    document_state_id = models.IntegerField(primary_key=True)
    document_state_val = models.CharField(blank=True, maxlength=150)
    equiv_group_flag = models.IntegerField(null=True, blank=True)
    document_desc = models.TextField(blank=True)
    class Meta:
        db_table = 'ref_doc_states_new'

class RefNextStatesNew(models.Model):
    id = models.IntegerField(primary_key=True)
    cur_state_id = models.IntegerField()
    next_state_id = models.IntegerField()
    condition = models.TextField(blank=True)
    class Meta:
        db_table = 'ref_next_states_new'

class RefResp(models.Model):
    ref_resp_id = models.IntegerField(primary_key=True)
    ref_resp_val = models.TextField(blank=True)
    class Meta:
        db_table = 'ref_resp'

class ReplacedIds(models.Model):
    id_document_tag = models.IntegerField(null=True, blank=True)
    replaced_by = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'replaced_ids'

class Request(models.Model):
    id_document_tag = models.IntegerField(unique=True)
    status_date = models.DateField(null=True, blank=True)
    rfc_flag = models.IntegerField(null=True, blank=True)
    intended_status_id = models.TextField(blank=True)
    area_acronym = models.TextField(blank=True)
    class Meta:
        db_table = 'request'

class RfcAuthors(models.Model):
    id = models.IntegerField(primary_key=True)
    rfc_number = models.IntegerField(unique=True)
    person_or_org_tag = models.IntegerField(unique=True)
    class Meta:
        db_table = 'rfc_authors'

class RfcIntendStatus(models.Model):
    intended_status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'rfc_intend_status'

class RfcStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status_value = models.TextField()
    class Meta:
        db_table = 'rfc_status'

class Rfcs(models.Model):
    rfc_number = models.IntegerField(primary_key=True)
    rfc_name = models.CharField(maxlength=600)
    rfc_name_key = models.CharField(maxlength=600)
    group_acronym = models.CharField(blank=True, maxlength=24)
    area_acronym = models.CharField(blank=True, maxlength=24)
    status_id = models.IntegerField()
    intended_status_id = models.IntegerField()
    fyi_number = models.CharField(blank=True, maxlength=60)
    std_number = models.CharField(blank=True, maxlength=60)
    txt_page_count = models.IntegerField(null=True, blank=True)
    online_version = models.TextField(blank=True)
    rfc_published_date = models.DateField(null=True, blank=True)
    proposed_date = models.DateField(null=True, blank=True)
    draft_date = models.DateField(null=True, blank=True)
    standard_date = models.DateField(null=True, blank=True)
    historic_date = models.DateField(null=True, blank=True)
    lc_sent_date = models.DateField(null=True, blank=True)
    lc_expiration_date = models.DateField(null=True, blank=True)
    b_sent_date = models.DateField(null=True, blank=True)
    b_approve_date = models.DateField(null=True, blank=True)
    comments = models.TextField(blank=True)
    last_modified_date = models.DateField()
    class Meta:
        db_table = 'rfcs'

class RfcsObsolete(models.Model):
    id = models.IntegerField(primary_key=True)
    rfc_number = models.IntegerField()
    action = models.TextField(unique=True)
    rfc_acted_on = models.IntegerField()
    class Meta:
        db_table = 'rfcs_obsolete'

class RollCall(models.Model):
    telechat_id = models.IntegerField(primary_key=True)
    person_or_org_tag = models.IntegerField(primary_key=True)
    attended = models.IntegerField(null=True, blank=True)
    wg_spoken = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'roll_call'

class ScheduledAnnouncements(models.Model):
    id = models.IntegerField(primary_key=True)
    mail_sent = models.IntegerField(null=True, blank=True)
    to_be_sent_date = models.DateField(null=True, blank=True)
    to_be_sent_time = models.CharField(blank=True, maxlength=150)
    scheduled_by = models.CharField(blank=True, maxlength=300)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.CharField(blank=True, maxlength=150)
    subject = models.CharField(blank=True, maxlength=765)
    to_val = models.CharField(blank=True, maxlength=765)
    from_val = models.CharField(blank=True, maxlength=765)
    cc_val = models.TextField(blank=True)
    body = models.TextField(blank=True)
    actual_sent_date = models.DateField(null=True, blank=True)
    actual_sent_time = models.CharField(blank=True, maxlength=150)
    first_q = models.IntegerField(null=True, blank=True)
    second_q = models.IntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    content_type = models.CharField(blank=True, maxlength=765)
    replyto = models.CharField(blank=True, maxlength=765)
    bcc_val = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'scheduled_announcements'

class ScheduledAnnouncementsTemp(models.Model):
    id = models.IntegerField(primary_key=True)
    mail_sent = models.IntegerField(null=True, blank=True)
    to_be_sent_date = models.DateField(null=True, blank=True)
    to_be_sent_time = models.CharField(blank=True, maxlength=150)
    scheduled_by = models.CharField(blank=True, maxlength=300)
    scheduled_date = models.DateField(null=True, blank=True)
    scheduled_time = models.CharField(blank=True, maxlength=150)
    subject = models.CharField(blank=True, maxlength=765)
    to_val = models.CharField(blank=True, maxlength=765)
    from_val = models.CharField(blank=True, maxlength=765)
    cc_val = models.CharField(blank=True, maxlength=765)
    body = models.TextField(blank=True)
    replyto = models.CharField(blank=True, maxlength=765)
    bcc_val = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'scheduled_announcements_temp'

class SdoChairs(models.Model):
    id = models.IntegerField(primary_key=True)
    sdo_id = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    email_priority = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'sdo_chairs'

class Sdos(models.Model):
    sdo_id = models.IntegerField(primary_key=True)
    sdo_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'sdos'

class SecretariatStaff(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    title = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'secretariat_staff'

class SessionConflicts(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    conflict_gid = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'session_conflicts'

class SessionNames(models.Model):
    session_name_id = models.IntegerField(primary_key=True)
    session_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'session_names'

class SessionRequestActivities(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    activity = models.TextField(blank=True)
    act_date = models.DateField(null=True, blank=True)
    act_time = models.CharField(blank=True, maxlength=300)
    act_by = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'session_request_activities'

class SessionStatus(models.Model):
    status_id = models.IntegerField(primary_key=True)
    status = models.CharField(blank=True, maxlength=300)
    class Meta:
        db_table = 'session_status'

class SlideTypes(models.Model):
    type_id = models.IntegerField(primary_key=True)
    type_name = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'slide_types'

class Slides(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    slide_num = models.IntegerField(null=True, blank=True)
    slide_type_id = models.IntegerField(null=True, blank=True)
    slide_name = models.CharField(blank=True, maxlength=765)
    irtf = models.IntegerField(null=True, blank=True)
    interim = models.IntegerField(null=True, blank=True)
    order_num = models.IntegerField(null=True, blank=True)
    in_q = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'slides'

class StaffWorkDetail(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=True, maxlength=765)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    actual_finish_date = models.DateField(null=True, blank=True)
    duration = models.CharField(blank=True, maxlength=765)
    percent_complete = models.CharField(blank=True, maxlength=765)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'staff_work_detail'

class StaffWorkHistory(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    history_text = models.TextField(blank=True)
    class Meta:
        db_table = 'staff_work_history'

class SubState(models.Model):
    sub_state_id = models.IntegerField(primary_key=True)
    sub_state_val = models.CharField(blank=True, maxlength=165)
    sub_state_desc = models.TextField(blank=True)
    class Meta:
        db_table = 'sub_state'

class Switches(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(blank=True, maxlength=300)
    val = models.IntegerField(null=True, blank=True)
    updated_date = models.DateField(null=True, blank=True)
    updated_time = models.TextField(blank=True) # This field type is a guess.
    class Meta:
        db_table = 'switches'

class TaskStatus(models.Model):
    task_status_id = models.IntegerField(primary_key=True)
    task_status_value = models.CharField(blank=True, maxlength=225)
    class Meta:
        db_table = 'task_status'

class Telechat(models.Model):
    telechat_id = models.IntegerField(primary_key=True)
    telechat_date = models.DateField(null=True, blank=True)
    minute_approved = models.IntegerField(null=True, blank=True)
    wg_news_txt = models.TextField(blank=True)
    iab_news_txt = models.TextField(blank=True)
    management_issue = models.TextField(blank=True)
    frozen = models.IntegerField(null=True, blank=True)
    mi_frozen = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'telechat'

class TelechatDates(models.Model):
    date1 = models.DateField(null=True, blank=True)
    date2 = models.DateField(null=True, blank=True)
    date3 = models.DateField(null=True, blank=True)
    date4 = models.DateField(null=True, blank=True)
    class Meta:
        db_table = 'telechat_dates'

class TelechatMinutes(models.Model):
    id = models.IntegerField(primary_key=True)
    telechat_date = models.DateField(null=True, blank=True)
    telechat_minute = models.TextField(blank=True)
    exported = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'telechat_minutes'

class TelechatUsers(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    is_iesg = models.IntegerField(null=True, blank=True)
    affiliated_org = models.CharField(blank=True, maxlength=75)
    class Meta:
        db_table = 'telechat_users'

class TempAdmins(models.Model):
    name = models.CharField(blank=True, maxlength=765)
    list_url = models.TextField(blank=True)
    class Meta:
        db_table = 'temp_admins'

class TempIdAuthors(models.Model):
    id = models.IntegerField(primary_key=True)
    id_document_tag = models.IntegerField()
    first_name = models.CharField(blank=True, maxlength=765)
    last_name = models.CharField(blank=True, maxlength=765)
    email_address = models.CharField(blank=True, maxlength=765)
    last_modified_date = models.DateField(null=True, blank=True)
    last_modified_time = models.CharField(blank=True, maxlength=300)
    author_order = models.IntegerField(null=True, blank=True)
    submission_id = models.IntegerField()
    class Meta:
        db_table = 'temp_id_authors'

class TempTelechatAttendees(models.Model):
    id = models.IntegerField(primary_key=True)
    telechat_id = models.IntegerField(null=True, blank=True)
    last_name = models.CharField(blank=True, maxlength=765)
    first_name = models.CharField(blank=True, maxlength=765)
    affiliation = models.CharField(blank=True, maxlength=765)
    class Meta:
        db_table = 'temp_telechat_attendees'

class TempTxt(models.Model):
    id = models.IntegerField(primary_key=True)
    temp_txt = models.TextField(blank=True)
    class Meta:
        db_table = 'temp_txt'

class Templates(models.Model):
    template_id = models.IntegerField(primary_key=True)
    template_text = models.TextField(blank=True)
    template_type = models.IntegerField(null=True, blank=True)
    template_title = models.CharField(blank=True, maxlength=765)
    note = models.TextField(blank=True)
    discussed_status_id = models.IntegerField(null=True, blank=True)
    decision = models.TextField(blank=True)
    class Meta:
        db_table = 'templates'

class UpdatedIpr(models.Model):
    id = models.IntegerField(primary_key=True)
    ipr_id = models.IntegerField(null=True, blank=True)
    status_to_be = models.IntegerField(null=True, blank=True)
    updated = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'updated_ipr'

class Uploads(models.Model):
    file_id = models.IntegerField(primary_key=True)
    file_title = models.CharField(blank=True, maxlength=765)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    file_extension = models.CharField(blank=True, maxlength=30)
    detail_id = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'uploads'

class UploadsTemp(models.Model):
    file_id = models.IntegerField(primary_key=True)
    file_title = models.CharField(blank=True, maxlength=765)
    file_extension = models.CharField(blank=True, maxlength=30)
    detail_id = models.IntegerField(null=True, blank=True)
    person_or_org_tag = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'uploads_temp'

class Users(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    login_name = models.CharField(blank=True, maxlength=765)
    password = models.CharField(blank=True, maxlength=75)
    user_level = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    class Meta:
        db_table = 'users'

class WebGmChairs(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    ip_address = models.TextField()
    gm_id = models.IntegerField()
    date = models.DateField()
    class Meta:
        db_table = 'web_gm_chairs'

class WebLoginInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    username = models.TextField()
    user_type = models.TextField()
    ip_address = models.TextField()
    date = models.DateField()
    class Meta:
        db_table = 'web_login_info'

class WebUserInfo(models.Model):
    id = models.IntegerField(primary_key=True)
    user_type = models.TextField()
    password = models.TextField()
    class Meta:
        db_table = 'web_user_info'

class WgAgenda(models.Model):
    id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    filename = models.CharField(blank=True, maxlength=765)
    irtf = models.IntegerField(null=True, blank=True)
    interim = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'wg_agenda'

class WgMeetingSessions(models.Model):
    session_id = models.IntegerField(primary_key=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    irtf = models.IntegerField(null=True, blank=True)
    num_session = models.IntegerField(null=True, blank=True)
    length_session1 = models.CharField(blank=True, maxlength=300)
    length_session2 = models.CharField(blank=True, maxlength=300)
    length_session3 = models.CharField(blank=True, maxlength=300)
    conflict1 = models.CharField(blank=True, maxlength=765)
    conflict2 = models.CharField(blank=True, maxlength=765)
    conflict3 = models.CharField(blank=True, maxlength=765)
    conflict_other = models.TextField(blank=True)
    special_req = models.TextField(blank=True)
    number_attendee = models.IntegerField(null=True, blank=True)
    approval_ad = models.IntegerField(null=True, blank=True)
    status_id = models.IntegerField(null=True, blank=True)
    ts_status_id = models.IntegerField(null=True, blank=True)
    requested_date = models.DateField(null=True, blank=True)
    approved_date = models.DateField(null=True, blank=True)
    requested_by = models.IntegerField(null=True, blank=True)
    scheduled_date = models.DateField(null=True, blank=True)
    last_modified_date = models.DateField(null=True, blank=True)
    ad_comments = models.TextField(blank=True)
    sched_room_id1 = models.IntegerField(null=True, blank=True)
    sched_time_id1 = models.IntegerField(null=True, blank=True)
    sched_date1 = models.DateField(null=True, blank=True)
    sched_room_id2 = models.IntegerField(null=True, blank=True)
    sched_time_id2 = models.IntegerField(null=True, blank=True)
    sched_date2 = models.DateField(null=True, blank=True)
    sched_room_id3 = models.IntegerField(null=True, blank=True)
    sched_time_id3 = models.IntegerField(null=True, blank=True)
    sched_date3 = models.DateField(null=True, blank=True)
    special_agenda_note = models.CharField(blank=True, maxlength=765)
    combined_room_id1 = models.IntegerField(null=True, blank=True)
    combined_time_id1 = models.IntegerField(null=True, blank=True)
    combined_room_id2 = models.IntegerField(null=True, blank=True)
    combined_time_id2 = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'wg_meeting_sessions'

class WgMeetingSessionsTemp(models.Model):
    temp_id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    irtf = models.IntegerField(null=True, blank=True)
    num_session = models.IntegerField(null=True, blank=True)
    length_session1 = models.CharField(blank=True, maxlength=300)
    length_session2 = models.CharField(blank=True, maxlength=300)
    length_session3 = models.CharField(blank=True, maxlength=300)
    conflict1 = models.CharField(blank=True, maxlength=765)
    conflict2 = models.CharField(blank=True, maxlength=765)
    conflict3 = models.CharField(blank=True, maxlength=765)
    conflict_other = models.TextField(blank=True)
    special_req = models.TextField(blank=True)
    number_attendee = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'wg_meeting_sessions_temp'

class WgPassword(models.Model):
    person_or_org_tag = models.IntegerField(primary_key=True)
    password = models.CharField(blank=True, maxlength=765)
    secrete_question_id = models.IntegerField(null=True, blank=True)
    secrete_answer = models.CharField(blank=True, maxlength=765)
    is_tut_resp = models.IntegerField(null=True, blank=True)
    irtf_id = models.IntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)
    login_name = models.CharField(blank=True, maxlength=300)
    class Meta:
        db_table = 'wg_password'

class WgProceedingsActivities(models.Model):
    id = models.IntegerField(primary_key=True)
    group_acronym_id = models.IntegerField(null=True, blank=True)
    meeting_num = models.IntegerField(null=True, blank=True)
    activity = models.CharField(blank=True, maxlength=765)
    act_date = models.DateField(null=True, blank=True)
    act_time = models.CharField(blank=True, maxlength=300)
    act_by = models.IntegerField(null=True, blank=True)
    class Meta:
        db_table = 'wg_proceedings_activities'

