#!/usr/bin/python

import sys, os, re, datetime

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path = [ basedir ] + sys.path

from ietf import settings
settings.USE_DB_REDESIGN_PROXY_CLASSES = False

from django.core import management
management.setup_environ(settings)

from redesign.doc.models import *
from redesign.group.models import *
from redesign.name.models import *
from ietf.idtracker.models import InternetDraft, IESGLogin, DocumentComment, PersonOrOrgInfo, RfcObsolete
from ietf.idrfc.models import RfcIndex, DraftVersions

import sys

document_name_to_import = None
if len(sys.argv) > 1:
    document_name_to_import = sys.argv[1]

# assumptions:
# - groups have been imported
# - IESG login emails/roles have been imported

# FIXME: what about RFCs

# Regarding history, we currently don't try to create DocumentHistory
# objects, we just import the comments as events.

# imports InternetDraft, IDInternal, BallotInfo, Position,
# IESGComment, IESGDiscuss, DocumentComment, RfcObsolete,
# idrfc.RfcIndex, idrfc.DraftVersions

def name(name_class, slug, name, desc=""):
    # create if it doesn't exist, set name and desc
    obj, _ = name_class.objects.get_or_create(slug=slug)
    obj.name = name
    obj.desc = desc
    obj.save()
    return obj

def alias_doc(name, doc):
    DocAlias.objects.filter(name=name).exclude(document=doc).delete()
    alias, _ = DocAlias.objects.get_or_create(name=name, document=doc)
    return alias

type_draft = name(DocTypeName, "draft", "Draft")
stream_ietf = name(DocStreamName, "ietf", "IETF")

relationship_replaces = name(DocRelationshipName, "replaces", "Replaces")
relationship_updates = name(DocRelationshipName, "updates", "Updates")
relationship_obsoletes = name(DocRelationshipName, "obs", "Obsoletes")

intended_status_mapping = {
    "BCP": name(IntendedStatusName, "bcp", "Best Current Practice"),
    "Draft Standard": name(IntendedStatusName, "ds", name="Draft Standard"),
    "Experimental": name(IntendedStatusName, "exp", name="Experimental"),
    "Historic": name(IntendedStatusName, "hist", name="Historic"),
    "Informational": name(IntendedStatusName, "inf", name="Informational"),
    "Proposed Standard": name(IntendedStatusName, "ps", name="Proposed Standard"),
    "Standard": name(IntendedStatusName, "std", name="Standard"),
    "None": None,
    "Request": None, # FIXME: correct? from idrfc_wrapper.py
    }

status_mapping = {
    'Active': name(DocStateName, "active", "Active"),
    'Expired': name(DocStateName, "expired", "Expired"),
    'RFC': name(DocStateName, "rfc", "RFC"),
    'Withdrawn by Submitter': name(DocStateName, "auth-rm", "Withdrawn by Submitter"),
    'Replaced': name(DocStateName, "repl", "Replaced"),
    'Withdrawn by IETF': name(DocStateName, "ietf-rm", "Withdrawn by IETF"),
    }

iesg_state_mapping = {
    'RFC Published': name(IesgDocStateName, "pub", "RFC Published", 'The ID has been published as an RFC.'),
    'Dead': name(IesgDocStateName, "dead", "Dead", 'Document is "dead" and is no longer being tracked. (E.g., it has been replaced by another document with a different name, it has been withdrawn, etc.)'),
    'Approved-announcement to be sent': name(IesgDocStateName, "approved", "Approved-announcement to be sent", 'The IESG has approved the document for publication, but the Secretariat has not yet sent out on official approval message.'),
    'Approved-announcement sent': name(IesgDocStateName, "ann", "Approved-announcement sent", 'The IESG has approved the document for publication, and the Secretariat has sent out the official approval message to the RFC editor.'),
    'AD is watching': name(IesgDocStateName, "watching", "AD is watching", 'An AD is aware of the document and has chosen to place the document in a separate state in order to keep a closer eye on it (for whatever reason). Documents in this state are still not being actively tracked in the sense that no formal request has been made to publish or advance the document. The sole difference between this state and "I-D Exists" is that an AD has chosen to put it in a separate state, to make it easier to keep track of (for the AD\'s own reasons).'),
    'IESG Evaluation': name(IesgDocStateName, "iesg-eva", "IESG Evaluation", 'The document is now (finally!) being formally reviewed by the entire IESG. Documents are discussed in email or during a bi-weekly IESG telechat. In this phase, each AD reviews the document and airs any issues they may have. Unresolvable issues are documented as "discuss" comments that can be forwarded to the authors/WG. See the description of substates for additional details about the current state of the IESG discussion.'),
    'AD Evaluation': name(IesgDocStateName, "ad-eval", "AD Evaluation", 'A specific AD (e.g., the Area Advisor for the WG) has begun reviewing the document to verify that it is ready for advancement. The shepherding AD is responsible for doing any necessary review before starting an IETF Last Call or sending the document directly to the IESG as a whole.'),
    'Last Call Requested': name(IesgDocStateName, "lc-req", "Last Call requested", 'The AD has requested that the Secretariat start an IETF Last Call, but the the actual Last Call message has not been sent yet.'),
    'In Last Call': name(IesgDocStateName, "lc", "In Last Call", 'The document is currently waiting for IETF Last Call to complete. Last Calls for WG documents typically last 2 weeks, those for individual submissions last 4 weeks.'),
    'Publication Requested': name(IesgDocStateName, "pub-req", "Publication Requested", 'A formal request has been made to advance/publish the document, following the procedures in Section 7.5 of RFC 2418. The request could be from a WG chair, from an individual through the RFC Editor, etc. (The Secretariat (iesg-secretary@ietf.org) is copied on these requests to ensure that the request makes it into the ID tracker.) A document in this state has not (yet) been reviewed by an AD nor has any official action been taken on it yet (other than to note that its publication has been requested.'),
    'RFC Ed Queue': name(IesgDocStateName, "rfcqueue", "RFC Ed Queue", 'The document is in the RFC editor Queue (as confirmed by http://www.rfc-editor.org/queue.html).'),
    'IESG Evaluation - Defer': name(IesgDocStateName, "defer", "IESG Evaluation - Defer", 'During a telechat, one or more ADs requested an additional 2 weeks to review the document. A defer is designed to be an exception mechanism, and can only be invoked once, the first time the document comes up for discussion during a telechat.'),
    'Waiting for Writeup': name(IesgDocStateName, "writeupw", "Waiting for Writeup", 'Before a standards-track or BCP document is formally considered by the entire IESG, the AD must write up a protocol action. The protocol action is included in the approval message that the Secretariat sends out when the document is approved for publication as an RFC.'),
    'Waiting for AD Go-Ahead': name(IesgDocStateName, "goaheadw", "Waiting for AD Go-Ahead", 'As a result of the IETF Last Call, comments may need to be responded to and a revision of the ID may be needed as well. The AD is responsible for verifying that all Last Call comments have been adequately addressed and that the (possibly revised) document is in the ID directory and ready for consideration by the IESG as a whole.'),
    'Expert Review': name(IesgDocStateName, "review-e", "Expert Review", 'An AD sometimes asks for an external review by an outside party as part of evaluating whether a document is ready for advancement. MIBs, for example, are reviewed by the "MIB doctors". Other types of reviews may also be requested (e.g., security, operations impact, etc.). Documents stay in this state until the review is complete and possibly until the issues raised in the review are addressed. See the "note" field for specific details on the nature of the review.'),
    'DNP-waiting for AD note': name(IesgDocStateName, "nopubadw", "DNP-waiting for AD note", 'Do Not Publish: The IESG recommends against publishing the document, but the writeup explaining its reasoning has not yet been produced. DNPs apply primarily to individual submissions received through the RFC editor.  See the "note" field for more details on who has the action item.'),
    'DNP-announcement to be sent': name(IesgDocStateName, "nopubanw", "DNP-announcement to be sent", 'The IESG recommends against publishing the document, the writeup explaining its reasoning has been produced, but the Secretariat has not yet sent out the official "do not publish" recommendation message.'),
    None: None, # FIXME: consider introducing the ID-exists state
    }

ballot_position_mapping = {
    'No Objection': name(BallotPositionName, 'noobj', 'No Objection'),
    'Yes': name(BallotPositionName, 'yes', 'Yes'),
    'Abstain': name(BallotPositionName, 'abstain', 'Abstain'),
    'Discuss': name(BallotPositionName, 'discuss', 'Discuss'),
    'Recuse': name(BallotPositionName, 'recuse', 'Recuse'),
    'Undefined': name(BallotPositionName, 'norecord', 'No record'),
    None: name(BallotPositionName, 'norecord', 'No record'),
    }

substate_mapping = {
    "External Party": name(DocInfoTagName, 'extpty', "External Party", 'The document is awaiting review or input from an external party (i.e, someone other than the shepherding AD, the authors, or the WG). See the "note" field for more details on who has the action.'),
    "Revised ID Needed": name(DocInfoTagName, 'need-rev', "Revised ID Needed", 'An updated ID is needed to address the issues that have been raised.'),
    "AD Followup": name(DocInfoTagName, 'ad-f-up', "AD Followup", """A generic substate indicating that the shepherding AD has the action item to determine appropriate next steps. In particular, the appropriate steps (and the corresponding next state or substate) depend entirely on the nature of the issues that were raised and can only be decided with active involvement of the shepherding AD. Examples include:

- if another AD raises an issue, the shepherding AD may first iterate with the other AD to get a better understanding of the exact issue. Or, the shepherding AD may attempt to argue that the issue is not serious enough to bring to the attention of the authors/WG.

- if a documented issue is forwarded to a WG, some further iteration may be needed before it can be determined whether a new revision is needed or whether the WG response to an issue clarifies the issue sufficiently.

- when a new revision appears, the shepherding AD will first look at the changes to determine whether they believe all outstanding issues have been raised satisfactorily, prior to asking the ADs who raised the original issues to verify the changes."""),
    "Point Raised - writeup needed": name(DocInfoTagName, 'point', "Point Raised - writeup needed", 'IESG discussions on the document have raised some issues that need to be brought to the attention of the authors/WG, but those issues have not been written down yet. (It is common for discussions during a telechat to result in such situations. An AD may raise a possible issue during a telechat and only decide as a result of that discussion whether the issue is worth formally writing up and bringing to the attention of the authors/WG). A document stays in the "Point Raised - Writeup Needed" state until *ALL* IESG comments that have been raised have been documented.')
    }

tag_review_by_rfc_editor = name(DocInfoTagName, 'rfc-rev', "Review by RFC Editor")
tag_via_rfc_editor = name(DocInfoTagName, 'via-rfc', "Via RFC Editor")
tag_expired_tombstone = name(DocInfoTagName, 'exp-tomb', "Expired tombstone")
tag_approved_in_minute = name(DocInfoTagName, 'app-min', "Approved in minute")

# helpers for events

def save_event(doc, event, comment):
    event.time = comment.datetime()
    event.by = iesg_login_to_email(comment.created_by)
    event.doc = doc
    if not event.desc:
        event.desc = comment.comment_text # FIXME: consider unquoting here
    event.save()

buggy_iesg_logins_cache = {}

# make sure system email exists
system_email, _ = Email.objects.get_or_create(address="(System)")

def iesg_login_to_email(l):
    if not l:
        return system_email
    else:
         # there's a bunch of old weird comments made by "IESG
         # Member", transform these into "System" instead
        if l.id == 2:
            return system_email
        
        # fix logins without the right person
        if not l.person:
            if l.id not in buggy_iesg_logins_cache:
                logins = IESGLogin.objects.filter(first_name=l.first_name, last_name=l.last_name).exclude(id=l.id)
                if logins:
                    buggy_iesg_logins_cache[l.id] = logins[0]
                else:
                    persons = PersonOrOrgInfo.objects.filter(first_name=l.first_name, last_name=l.last_name)
                    if persons:
                        l.person = persons[0]
                        buggy_iesg_logins_cache[l.id] = l
                    else:
                        buggy_iesg_logins_cache[l.id] = None
            l = buggy_iesg_logins_cache[l.id]
            
        try:
            return Email.objects.get(address=l.person.email()[1])
        except Email.DoesNotExist:
            try:
                return Email.objects.get(person__name="%s %s" % (l.person.first_name, l.person.last_name))
            except Email.DoesNotExist:
                print "MISSING IESG LOGIN", l.person.email()
                return None

# regexps for parsing document comments

date_re_str = "(?P<year>[0-9][0-9][0-9][0-9])-(?P<month>[0-9][0-9])-(?P<day>[0-9][0-9])"
def date_in_match(match):
    return datetime.date(int(match.group('year')), int(match.group('month')), int(match.group('day')))

re_telechat_agenda = re.compile(r"(Placed on|Removed from) agenda for telechat(| - %s) by" % date_re_str)
re_telechat_changed = re.compile(r"Telechat date (was|has been) changed to (<b>)?%s(</b>)? from" % date_re_str)
re_ballot_position = re.compile(r"\[Ballot Position Update\] (New position, (?P<position>.*), has been recorded (|for (?P<for>.*) )|Position (|for (?P<for2>.*) )has been changed to (?P<position2>.*) from .*)by (?P<by>.*)")
re_ballot_issued = re.compile(r"Ballot has been issued(| by)")
re_state_changed = re.compile(r"(State (has been changed|changed|Changes) to <b>(?P<to>.*)</b> from <b>(?P<from>.*)</b> by|Sub state has been changed to (?P<tosub>.*) from (?P<fromsub>.*))")
re_note_changed = re.compile(r"(\[Note\]: .*'.*'|Note field has been cleared)", re.DOTALL)
re_draft_added = re.compile(r"Draft [Aa]dded (by .*)?( in state (?P<state>.*))?")
re_last_call_requested = re.compile(r"Last Call was requested")
re_document_approved = re.compile(r"IESG has approved and state has been changed to")
re_document_disapproved = re.compile(r"(Do Not Publish|DNP) note has been sent to RFC Editor and state has been changed to")
re_resurrection_requested = re.compile(r"(I-D |)Resurrection was requested by")
re_completed_resurrect = re.compile(r"(This document has been resurrected|This document has been resurrected per RFC Editor's request|Resurrection was completed)")

re_status_date_changed = re.compile(r"Status [dD]ate has been changed to (<b>)?" + date_re_str)
re_responsible_ad_changed = re.compile(r"(Responsible AD|Shepherding AD|responsible) has been changed to (<b>)?")
re_intended_status_changed = re.compile(r"Intended [sS]tatus has been changed to (<b>)?")
re_state_change_notice = re.compile(r"State Change Notice email list (have been change|has been changed) (<b>)?")
re_area_acronym_changed = re.compile(r"Area acronymn? has been changed to \w+ from \w+(<b>)?")

all_drafts = InternetDraft.objects.all().select_related()
if document_name_to_import:
    all_drafts = all_drafts.filter(filename=document_name_to_import)
#all_drafts = all_drafts[all_drafts.count() - 1000:]

for o in all_drafts:
    try:
        d = Document.objects.get(name=o.filename)
    except Document.DoesNotExist:
        d = Document(name=o.filename)
        
    d.time = o.idinternal.event_date if o.idinternal else o.revision_date
    d.type = type_draft
    d.title = o.title
    d.state = status_mapping[o.status.status]
    d.group = Group.objects.get(acronym=o.group.acronym)
    d.stream = stream_ietf
    d.wg_state = None
    d.iesg_state = iesg_state_mapping[o.idinternal.cur_state.state if o.idinternal else None]
    # we currently ignore the previous IESG state prev_state
    d.iana_state = None
#    d.rfc_state = # FIXME
    d.rev = o.revision
    d.abstract = o.abstract
    d.pages = o.txt_page_count
    d.intended_std_level = intended_status_mapping[o.intended_status.intended_status]
#    d.std_level = # FIXME
#    d.authors =
#    d.related = # FIXME
    d.ad = iesg_login_to_email(o.idinternal.job_owner) if o.idinternal else None
    d.shepherd = None
    d.notify = o.idinternal.state_change_notice_to or "" if o.idinternal else ""
    d.external_url = ""
    d.note = o.idinternal.note or "" if o.idinternal else ""
    d.internal_comments = o.comments or "" # FIXME: maybe put these somewhere else
    d.save()

    # make sure our alias is updated
    alias_doc(d.name, d)
    
    # clear already imported events
    d.event_set.all().delete()
    
    if o.idinternal:
        last_note_change_text = ""
        
        # extract events
        for c in o.idinternal.documentcomment_set.order_by('date', 'time', 'id'):
            handled = False
            
            # telechat agenda schedulings
            match = re_telechat_agenda.search(c.comment_text) or re_telechat_changed.search(c.comment_text)
            if match:
                e = Telechat()
                e.type = "scheduled_for_telechat"
                e.telechat_date = date_in_match(match) if "Placed on" in c.comment_text else None
                # can't extract this from history so we just take the latest value
                e.returning_item = bool(o.idinternal.returning_item)
                save_event(d, e, c)
                handled = True
                
            # ballot issued
            match = re_ballot_issued.search(c.comment_text)
            if match:
                e = Text()
                e.type = "sent_ballot_announcement"
                save_event(d, e, c)

                # when you issue a ballot, you also vote yes; add that vote
                e = BallotPosition()
                e.type = "changed_ballot_position"
                e.ad = iesg_login_to_email(c.created_by)
                e.desc = "[Ballot Position Update] New position, Yes, has been recorded by %s" % e.ad.get_name()
                last_pos = d.latest_event(type="changed_ballot_position", ballotposition__ad=e.ad)
                e.pos = ballot_position_mapping["Yes"]
                e.discuss = last_pos.ballotposition.discuss if last_pos else ""
                e.discuss_time = last_pos.ballotposition.discuss_time if last_pos else None
                e.comment = last_pos.ballotposition.comment if last_pos else ""
                e.comment_time = last_pos.ballotposition.comment_time if last_pos else None
                save_event(d, e, c)
                handled = True
                
            # ballot positions
            match = re_ballot_position.search(c.comment_text)
            if match:
                position = match.group('position') or match.group('position2')
                ad_name = match.group('for') or match.group('for2') or match.group('by') # some of the old positions don't specify who it's for, in that case assume it's "by", the person who entered the position
                ad_first, ad_last = ad_name.split(' ')

                e = BallotPosition()
                e.type = "changed_ballot_position"
                e.ad = iesg_login_to_email(IESGLogin.objects.get(first_name=ad_first, last_name=ad_last))
                last_pos = d.latest_event(type="changed_ballot_position", ballotposition__ad=e.ad)
                e.pos = ballot_position_mapping[position]
                e.discuss = last_pos.ballotposition.discuss if last_pos else ""
                e.discuss_time = last_pos.ballotposition.discuss_time if last_pos else None
                e.comment = last_pos.ballotposition.comment if last_pos else ""
                e.comment_time = last_pos.ballotposition.comment_time if last_pos else None
                save_event(d, e, c)
                handled = True

            # ballot discusses/comments
            if c.ballot in (DocumentComment.BALLOT_DISCUSS, DocumentComment.BALLOT_COMMENT):
                e = BallotPosition()
                e.type = "changed_ballot_position"
                e.ad = iesg_login_to_email(c.created_by)
                last_pos = d.latest_event(type="changed_ballot_position", ballotposition__ad=e.ad)
                e.pos = last_pos.ballotposition.pos if last_pos else ballot_position_mapping[None]
                if c.ballot == DocumentComment.BALLOT_DISCUSS:
                    e.discuss = c.comment_text
                    e.discuss_time = c.datetime()
                    e.comment = last_pos.ballotposition.comment if last_pos else ""
                    e.comment_time = last_pos.ballotposition.comment_time if last_pos else None
                    # put header into description
                    c.comment_text = "[Ballot discuss]\n" + c.comment_text
                else:
                    e.discuss = last_pos.ballotposition.discuss if last_pos else ""
                    e.discuss_time = last_pos.ballotposition.discuss_time if last_pos else None
                    e.comment = c.comment_text
                    e.comment_time = c.datetime()
                    # put header into description
                    c.comment_text = "[Ballot comment]\n" + c.comment_text
                save_event(d, e, c)
                handled = True

            # last call requested
            match = re_last_call_requested.search(c.comment_text)
            if match:
                e = Event(type="requested_last_call")
                save_event(d, e, c)
                handled = True

            # state changes
            match = re_state_changed.search(c.comment_text)
            if match:
                e = Event(type="changed_document")
                save_event(d, e, c)
                handled = True

            # note changed
            match = re_note_changed.search(c.comment_text)
            if match:
                # watch out for duplicates of which the old data's got many
                if c.comment_text != last_note_change_text:
                    last_note_change_text = c.comment_text
                    e = Event(type="changed_document")
                    save_event(d, e, c)
                handled = True

            # draft added 
            match = re_draft_added.search(c.comment_text)
            if match:
                e = Event(type="changed_document")
                save_event(d, e, c)
                handled = True

            # new version
            if c.comment_text == "New version available":
                e = NewRevision(type="new_revision", rev=c.version)
                save_event(d, e, c)
                handled = True

            # resurrect requested
            match = re_resurrection_requested.search(c.comment_text)
            if match:
                e = Event(type="requested_resurrect")
                save_event(d, e, c)
                handled = True
                
            # completed resurrect
            match = re_completed_resurrect.search(c.comment_text)
            if match:
                e = Event(type="completed_resurrect")
                save_event(d, e, c)
                handled = True
                
            # document expiration
            if c.comment_text == "Document is expired by system":
                e = Event(type="expired_document")
                save_event(d, e, c)
                handled = True

            # approved document 
            match = re_document_approved.search(c.comment_text)
            if match:
                e = Event(type="iesg_approved")
                save_event(d, e, c)
                handled = True

            # disapproved document
            match = re_document_disapproved.search(c.comment_text)
            if match:
                e = Event(type="iesg_disapproved")
                save_event(d, e, c)
                handled = True
                

            # some changes can be bundled - this is not entirely
            # convenient, especially since it makes it hard to give
            # each a type, so unbundle them
            if not handled:
                unhandled_lines = []
                for line in c.comment_text.split("<br>"):
                    # status date changed
                    match = re_status_date_changed.search(line)
                    if match:
                        e = Status(type="changed_status_date", date=date_in_match(match))
                        e.desc = line
                        save_event(d, e, c)
                        handled = True

                    # AD/job owner changed
                    match = re_responsible_ad_changed.search(line)
                    if match:
                        e = Event(type="changed_document")
                        e.desc = line
                        save_event(d, e, c)
                        handled = True

                    # intended standard level changed
                    match = re_intended_status_changed.search(line)
                    if match:
                        e = Event(type="changed_document")
                        e.desc = line
                        save_event(d, e, c)
                        handled = True

                    # state change notice
                    match = re_state_change_notice.search(line)
                    if match:
                        e = Event(type="changed_document")
                        e.desc = line
                        save_event(d, e, c)
                        handled = True

                    # area acronym
                    match = re_area_acronym_changed.search(line)
                    if match:
                        e = Event(type="changed_document")
                        e.desc = line
                        save_event(d, e, c)
                        handled = True

                    # multiline change bundles end with a single "by xyz" that we skip
                    if not handled and not line.startswith("by <b>"):
                        unhandled_lines.append(line)
                        
                if handled:
                    c.comment_text = "<br>".join(unhandled_lines)

                    if c.comment_text:
                        print "couldn't handle multi-line comment %s '%s'" % (c.id, c.comment_text.replace("\n", " ").replace("\r", "")[0:80])
                
            # all others are added as comments
            if not handled:
                e = Event(type="added_comment")
                save_event(d, e, c)

                # stop typical comments from being output
                typical_comments = [
                    "Document Shepherd Write-up for %s" % d.name,
                    "Who is the Document Shepherd for this document",
                    "We understand that this document doesn't require any IANA actions",
                    "IANA questions",
                    "IANA has questions",
                    "IANA comments",
                    "IANA Comments",
                    "IANA Evaluation Comments",
                                    ]
                for t in typical_comments:
                    if t in c.comment_text:
                        handled = True
                        break
            
            if not handled:
                print "couldn't handle comment %s '%s'" % (c.id, c.comment_text.replace("\n", " ").replace("\r", "")[0:80])

                
    # import missing revision changes from DraftVersions
    known_revisions = set(e.newrevision.rev for e in d.event_set.filter(type="new_revision").select_related('newrevision'))
    for v in DraftVersions.objects.filter(filename=d.name).order_by("revision"):
        if v.revision not in known_revisions:
            e = NewRevision(type="new_revision")
            e.rev = v.revision
            # we don't have time information in this source, so
            # hack the seconds to include the revision to ensure
            # they're ordered correctly
            e.time = datetime.datetime.combine(v.revision_date, datetime.time(0, 0, int(v.revision)))
            e.by = system_email
            e.doc = d
            e.desc = "New version available"
            e.save()
            known_revisions.add(v.revision)
    
    # import events that might be missing, we can't be sure who did
    # them or when but if we don't generate them, we'll be missing the
    # information completely

    # make sure last decision is recorded
    e = d.latest_event(Event, type__in=("iesg_approved", "iesg_disapproved"))
    decision_date = e.time.date() if e else None
    if o.b_approve_date != decision_date:
        disapproved = o.idinternal and o.idinternal.dnp
        e = Event(type="iesg_disapproved" if disapproved else "iesg_approved")
        e.time = o.b_approve_date
        e.by = system_email
        e.doc = d
        e.desc = "Do Not Publish note has been sent to RFC Editor" if disapproved else "IESG has approved"
        e.save()

    if o.lc_expiration_date:
        e = Expiration(type="sent_last_call", expires=o.lc_expiration_date)
        # let's try to find the actual change
        events = d.event_set.filter(type="changed_document", desc__contains=" to <b>In Last Call</b>").order_by('-time')[:1]
        # event time is more accurate with actual time instead of just
        # date, gives better sorting
        e.time = events[0].time if events else o.lc_sent_date
        e.by = events[0].by if events else system_email
        e.doc = d
        e.desc = "Last call sent"
        e.save()

    if o.idinternal:
        made_up_date = d.latest_event().time + datetime.timedelta(seconds=1) # datetime.datetime(2030, 1, 1, 0, 0, 0)

        e = d.latest_event(Status, type="changed_status_date")
        status_date = e.date if e else None
        if o.idinternal.status_date != status_date:
            e = Status(type="changed_status_date", date=o.idinternal.status_date)
            e.time = made_up_date
            e.by = system_email
            e.doc = d
            e.desc = "Status date has been changed to <b>%s</b> from <b>%s</b>" % (o.idinternal.status_date, status_date)
            e.save()

        e = d.latest_event(Telechat, type="scheduled_for_telechat")
        telechat_date = e.telechat_date if e else None
        if not o.idinternal.agenda:
            o.idinternal.telechat_date = None # normalize

        if telechat_date != o.idinternal.telechat_date:
            e = Telechat(type="scheduled_for_telechat",
                         telechat_date=o.idinternal.telechat_date,
                         returning_item=bool(o.idinternal.returning_item))
            # a common case is that it has been removed from the
            # agenda automatically by a script without a notice in the
            # comments, in that case the time is simply the day after
            # the telechat
            e.time = telechat_date + datetime.timedelta(days=1) if telechat_date and not o.idinternal.telechat_date else made_up_date
            e.by = system_email
            args = ("Placed on", o.idinternal.telechat_date) if o.idinternal.telechat_date else ("Removed from", telechat_date)
            e.doc = d
            e.desc = "%s agenda for telechat - %s by system" % args
            e.save()

        if o.idinternal.ballot:
            text_date = made_up_date

            # if any of these events have happened, they're closer to
            # the real time
            e = d.event_set.filter(type__in=("requested_last_call", "sent_last_call", "sent_ballot_announcement", "iesg_approved", "iesg_disapproved")).order_by('time')[:1]
            if e:
                text_date = e[0].time - datetime.timedelta(seconds=1)
            
            if o.idinternal.ballot.approval_text:
                e = Text(type="changed_ballot_approval_text", content=o.idinternal.ballot.approval_text)
                e.time = text_date
                e.by = system_email
                e.doc = d
                e.desc = "Ballot approval text was added"
                e.save()

            if o.idinternal.ballot.last_call_text:
                e = Text(type="changed_last_call_text", content=o.idinternal.ballot.last_call_text)
                e.time = text_date
                e.by = system_email
                e.doc = d
                e.desc = "Last call text was added"
                e.save()

            if o.idinternal.ballot.ballot_writeup:
                e = Text(type="changed_ballot_writeup_text", content=o.idinternal.ballot.ballot_writeup)
                e.time = text_date
                e.by = system_email
                e.doc = d
                e.desc = "Ballot writeup text was added"
                e.save()

    # import other attributes

    # tags
    tags = d.tags.all()
    def sync_tag(include, tag):
        if include and tag not in tags:
            d.tags.add(tag)
        if not include and tag in tags:
            d.tags.remove(tag)

    sync_tag(o.review_by_rfc_editor, tag_review_by_rfc_editor)
    sync_tag(o.expired_tombstone, tag_expired_tombstone)
    sync_tag(o.idinternal and o.idinternal.via_rfc_editor, tag_via_rfc_editor)

    n = o.idinternal and o.idinternal.cur_sub_state and o.idinternal.cur_sub_state.sub_state
    for k, v in substate_mapping.iteritems():
        sync_tag(k == n, v)
        # currently we ignore prev_sub_state

    sync_tag(o.idinternal and o.idinternal.approved_in_minute, tag_approved_in_minute)
    
    # RFC alias
    if o.rfc_number:
        alias_doc("rfc%s" % o.rfc_number, d)
        # FIXME: some RFCs seem to be called rfc1234bis?
            
    if o.replaced_by:
        replacement, _ = Document.objects.get_or_create(name=o.replaced_by.filename)
        RelatedDocument.objects.get_or_create(document=replacement, doc_alias=d_alias, relationship=relationship_replaces)
    
    # the RFC-related attributes are imported when we handle the RFCs below
            
    print "imported", d.name, " - ", d.iesg_state


# now process RFCs

def get_or_create_rfc_document(rfc_number):
    name = "rfc%s" % rfc_number

    # try to find a draft that can form the base of the document
    draft = None

    ids = InternetDraft.objects.filter(rfc_number=rfc_number)[:1]
    if ids:
        draft = ids[0]
    else:
        r = RfcIndex.objects.get(rfc_number=rfc_number)
        # rfcindex occasionally includes drafts that were not
        # really submitted to IETF (e.g. April 1st)
        if r.draft:
            ids = InternetDraft.objects.filter(filename=r.draft)[:1]
            if ids:
                draft = ids[0]

    if draft:
        name = draft.filename

    d, _ = Document.objects.get_or_create(name=name)
    if not name.startswith('rfc'):
        # make sure draft also got an alias
        alias_doc(name, d)
        
    alias = alias_doc("rfc%s" % rfc_number, d)
    
    return (d, alias)
    
all_rfcs = RfcIndex.objects.all()

if all_drafts.count() != InternetDraft.objects.count():
    if document_name_to_import.startswith("rfc"):
        # we wanted to import just an RFC, great
        all_rfcs = all_rfcs.filter(rfc_number=document_name_to_import[3:])
    else:
        # if we didn't process all drafts, limit the RFCs to the ones we
        # did process
        all_rfcs = all_rfcs.filter(rfc_number__in=set(d.rfc_number for d in all_drafts if d.rfc_number))

for o in all_rfcs:
    d, d_alias = get_or_create_rfc_document(o.rfc_number)
    
    # import obsoletes/updates
    def make_relation(other_rfc, rel_type, reverse):
        other_number = int(other_rfc.replace("RFC", ""))
        other, other_alias = get_or_create_rfc_document(other_number)
        if reverse:
            RelatedDocument.objects.get_or_create(document=other, doc_alias=d_alias, relationship=rel_type)
        else:
            RelatedDocument.objects.get_or_create(document=d, doc_alias=other_alias, relationship=rel_type)

    if o.obsoletes:
        for x in o.obsoletes.split(','):
            make_relation(x, relationship_obsoletes, False)
    if o.obsoleted_by:
        for x in o.obsoleted_by.split(','):
            make_relation(x, relationship_obsoletes, True)
    if o.updates:
        for x in o.updates.split(','):
            make_relation(x, relationship_updates, False)
    if o.updated_by:
        for x in o.updated_by.split(','):
            make_relation(x, relationship_updates, True)

    if o.also:
        print o.also
        alias_doc(o.also.lower(), d)
            
    print "imported", d_alias.name, " - ", d.rfc_state


sys.exit(0)

class RfcIndex(models.Model):
#    rfc_number = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=250)
    authors = models.CharField(max_length=250)
    rfc_published_date = models.DateField()
    current_status = models.CharField(max_length=50,null=True)
#    updates = models.CharField(max_length=200,blank=True,null=True)
#    updated_by = models.CharField(max_length=200,blank=True,null=True)
#    obsoletes = models.CharField(max_length=200,blank=True,null=True)
#    obsoleted_by = models.CharField(max_length=200,blank=True,null=True)
#    also = models.CharField(max_length=50,blank=True,null=True)
    draft = models.CharField(max_length=200,null=True)
    has_errata = models.BooleanField()
    stream = models.CharField(max_length=15,blank=True,null=True)
    wg = models.CharField(max_length=15,blank=True,null=True)
    file_formats = models.CharField(max_length=20,blank=True,null=True)
