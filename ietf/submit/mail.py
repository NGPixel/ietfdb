import re
import email
import datetime

import pyzmail

from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from ietf.utils.log import log
from ietf.utils.mail import send_mail, send_mail_message
from ietf.doc.models import Document
from ietf.ipr.mail import utc_from_string
from ietf.mailtrigger.utils import gather_address_lists, \
    get_base_submission_message_address
from ietf.person.models import Person
from ietf.message.models import Message, MessageAttachment
from ietf.utils.accesstoken import generate_access_token
from ietf.submit.models import SubmissionEmail, Submission


def send_submission_confirmation(request, submission):
    subject = 'Confirm submission of I-D %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email, cc) = gather_address_lists('sub_confirmation_requested',submission=submission)

    confirm_url = settings.IDTRACKER_BASE_URL + urlreverse('submit_confirm_submission', kwargs=dict(submission_id=submission.pk, auth_token=generate_access_token(submission.auth_key)))
    status_url = settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status_by_hash', kwargs=dict(submission_id=submission.pk, access_token=submission.access_token()))
        
    send_mail(request, to_email, from_email, subject, 'submit/confirm_submission.txt', 
              {
                'submission': submission,
                'confirm_url': confirm_url,
                'status_url': status_url,
              },
              cc=cc)

    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_full_url(request, submission):
    subject = 'Full URL for managing submission of draft %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email, cc) = gather_address_lists('sub_management_url_requested',submission=submission)
    url = settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status_by_hash', kwargs=dict(submission_id=submission.pk, access_token=submission.access_token()))

    send_mail(request, to_email, from_email, subject, 'submit/full_url.txt', 
              {
                'submission': submission,
                'url': url,
              },
              cc=cc)

    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_approval_request_to_group(request, submission):
    subject = 'New draft waiting for approval: %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email,cc) = gather_address_lists('sub_chair_approval_requested',submission=submission)
    if not to_email:
        return to_email

    send_mail(request, to_email, from_email, subject, 'submit/approval_request.txt', 
              {
                'submission': submission,
                'domain': Site.objects.get_current().domain,
              },
              cc=cc)
    all_addrs = to_email
    all_addrs.extend(cc)
    return all_addrs

def send_manual_post_request(request, submission, errors):
    subject = u'Manual Post Requested for %s' % submission.name
    from_email = settings.IDSUBMIT_FROM_EMAIL
    (to_email,cc) = gather_address_lists('sub_manual_post_requested',submission=submission)
    send_mail(request, to_email, from_email, subject, 'submit/manual_post_request.txt', {
        'submission': submission,
        'url': settings.IDTRACKER_BASE_URL + urlreverse('submit_submission_status', kwargs=dict(submission_id=submission.pk)),
        'errors': errors,
    }, cc=cc)


def announce_to_lists(request, submission):
    m = Message()
    m.by = Person.objects.get(name="(System)")
    if request.user.is_authenticated():
        try:
            m.by = request.user.person
        except Person.DoesNotExist:
            pass
    m.subject = 'I-D Action: %s-%s.txt' % (submission.name, submission.rev)
    m.frm = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
    (m.to, m.cc) = gather_address_lists('sub_announced',submission=submission)
    m.body = render_to_string('submit/announce_to_lists.txt',
                              dict(submission=submission,
                                   settings=settings))
    m.save()
    m.related_docs.add(Document.objects.get(name=submission.name))

    send_mail_message(request, m)


def announce_new_version(request, submission, draft, state_change_msg):
    (to_email,cc) = gather_address_lists('sub_new_version',doc=draft,submission=submission)

    if to_email:
        subject = 'New Version Notification - %s-%s.txt' % (submission.name, submission.rev)
        from_email = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
        send_mail(request, to_email, from_email, subject, 'submit/announce_new_version.txt',
                  {'submission': submission,
                   'msg': state_change_msg},
                  cc=cc)

def announce_to_authors(request, submission):
    (to_email, cc) = gather_address_lists('sub_announced_to_authors',submission=submission)
    from_email = settings.IDSUBMIT_ANNOUNCE_FROM_EMAIL
    subject = 'New Version Notification for %s-%s.txt' % (submission.name, submission.rev)
    if submission.group:
        group = submission.group.acronym
    elif submission.name.startswith('draft-iesg'):
        group = 'IESG'
    else:
        group = 'Individual Submission'
    send_mail(request, to_email, from_email, subject, 'submit/announce_to_authors.txt',
              {'submission': submission,
               'group': group},
              cc=cc)


def process_response_email(msg):
    """Saves an incoming message.  msg=string.  Message "To" field is expected to
    be in the format ietf-submit+[identifier]@ietf.org.  Expect to find a message with
    a matching value in the reply_to field, associated to a submission.
    Create a Message object for the incoming message and associate it to
    the original message via new SubmissionEvent"""
    message = email.message_from_string(msg)
    to = message.get('To')

    # exit if this isn't a response we're interested in (with plus addressing)
    local,domain = get_base_submission_message_address().split('@')
    if not re.match(r'^{}\+[a-zA-Z0-9_\-]{}@{}'.format(local,'{16}',domain),to):
        return None

    try:
        to_message = Message.objects.get(reply_to=to)
    except Message.DoesNotExist:
        log('Error finding matching message ({})'.format(to))
        return None

    try:
        submission = to_message.manualevents.first().submission
    except:
        log('Error processing message ({})'.format(to))
        return None

    if not submission:
        log('Error processing message - no submission ({})'.format(to))
        return None

    parts = pyzmail.parse.get_mail_parts(message)
    body=''
    for part in parts:
        if part.is_body == 'text/plain' and part.disposition == None:
            payload, used_charset = pyzmail.decode_text(part.get_payload(), part.charset, None)
            body = body + payload + '\n'

    by = Person.objects.get(name="(System)")
    msg = submit_message_from_message(message, body, by)

    submission_email_event = SubmissionEmail.objects.create(
            submission = submission,
            msgtype = 'msgin',
            by = by,
            message = msg,
            in_reply_to = to_message
    )

    save_submission_email_attachments(submission_email_event, parts)

    log(u"Received submission email from %s" % msg.frm)
    return msg


def add_submission_email(remote_ip, name, submission_pk, message, by, msgtype):
    """Add email to submission history"""

    #in_reply_to = form.cleaned_data['in_reply_to']
    # create Message
    parts = pyzmail.parse.get_mail_parts(message)
    body=''
    for part in parts:
        if part.is_body == 'text/plain' and part.disposition == None:
            payload, used_charset = pyzmail.decode_text(part.get_payload(), part.charset, None)
            body = body + payload + '\n'

    msg = submit_message_from_message(message, body, by)

    if (submission_pk != None):
        # Must exist
        submission = Submission.objects.get(pk=submission_pk)
    else:
        # create Submission using the name
        try:
            submission = Submission.objects.create(
                    state_id="manual-awaiting-draft",
                    remote_ip=remote_ip,
                    name=name,
                    title=name,
                    note="",
                    submission_date=datetime.date.today(),
                    replaces="",
            )
        except Exception as e:
            log("Exception: %s\n" % e)
            raise

    submission_email_event = SubmissionEmail.objects.create(
            submission = submission,
            msgtype = msgtype,
            by = by,
            message = msg)
    #in_reply_to = in_reply_to

    save_submission_email_attachments(submission_email_event, parts)
    return submission, submission_email_event
        
        
def submit_message_from_message(message,body,by=None):
    """Returns a ietf.message.models.Message.  msg=email.Message
        A copy of mail.message_from_message with different body handling
    """
    if not by:
        by = Person.objects.get(name="(System)")
    msg = Message.objects.create(
            by = by,
            subject = message.get('subject',''),
            frm = message.get('from',''),
            to = message.get('to',''),
            cc = message.get('cc',''),
            bcc = message.get('bcc',''),
            reply_to = message.get('reply_to',''),
            body = body,
            time = utc_from_string(message['date'])
    )
    return msg

def save_submission_email_attachments(submission_email_event, parts):
    for part in parts:
        if part.disposition != 'attachment':
            continue

        payload, used_charset = pyzmail.decode_text(part.get_payload(), 
                                                    part.charset, 
                                                    None)

        #name = submission_email_event.submission.name

        MessageAttachment.objects.create(message = submission_email_event.message,
                                         filename=part.filename,
                                         body=payload)
