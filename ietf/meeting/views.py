# Copyright The IETF Trust 2007, All Rights Reserved

import datetime
import os
import re
import tarfile
import urllib
from tempfile import mkstemp
from collections import OrderedDict, Counter
import csv
import json
import pytz
from pyquery import PyQuery
from wsgiref.handlers import format_date_time
from calendar import timegm

import debug                            # pyflakes:ignore

from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse,reverse_lazy
from django.db.models import Min, Max, Q
from django.forms.models import modelform_factory, inlineformset_factory
from django.forms import ModelForm
from django.template import TemplateDoesNotExist
from django.template.loader import render_to_string
from django.utils.functional import curry
from django.views.decorators.cache import cache_page
from django.utils.text import slugify
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.generic import RedirectView


from ietf.doc.fields import SearchableDocumentsField
from ietf.doc.models import Document, State, DocEvent, NewRevisionDocEvent
from ietf.group.models import Group
from ietf.group.utils import can_manage_materials
from ietf.ietfauth.utils import role_required, has_role
from ietf.meeting.models import Meeting, Session, Schedule, Room, FloorPlan, SessionPresentation
from ietf.meeting.helpers import get_areas, get_person_by_email, get_schedule_by_name
from ietf.meeting.helpers import build_all_agenda_slices, get_wg_name_list
from ietf.meeting.helpers import get_all_assignments_from_schedule
from ietf.meeting.helpers import get_modified_from_assignments
from ietf.meeting.helpers import get_wg_list, find_ads_for_meeting
from ietf.meeting.helpers import get_meeting, get_schedule, agenda_permissions, get_meetings
from ietf.meeting.helpers import preprocess_assignments_for_agenda, read_agenda_file, read_session_file
from ietf.meeting.helpers import convert_draft_to_pdf, get_earliest_session_date
from ietf.meeting.helpers import can_view_interim_request, can_approve_interim_request
from ietf.meeting.helpers import can_edit_interim_request
from ietf.meeting.helpers import can_request_interim_meeting, get_announcement_initial
from ietf.meeting.helpers import sessions_post_save, is_meeting_approved
from ietf.meeting.helpers import send_interim_cancellation_notice
from ietf.meeting.helpers import send_interim_approval_request
from ietf.meeting.helpers import send_interim_announcement_request
from ietf.meeting.utils import finalize
from ietf.secr.proceedings.utils import handle_upload_file
from ietf.secr.proceedings.proc_utils import (get_progress_stats, post_process, import_audio_files,
    import_youtube_video_urls)
from ietf.utils.mail import send_mail_message
from ietf.utils.pipe import pipe
from ietf.utils.pdf import pdf_pages
from ietf.utils.text import xslugify
from ietf.utils.validators import ( validate_file_size, validate_mime_type,
    validate_file_extension, validate_no_html_frame, )

from .forms import (InterimMeetingModelForm, InterimAnnounceForm, InterimSessionModelForm,
    InterimCancelForm, InterimSessionInlineFormSet)


def get_menu_entries(request):
    '''Setup menu entries for interim meeting view tabs'''
    entries = []
    if has_role(request.user, ('Area Director','Secretariat','IRTF Chair','WG Chair', 'RG Chair')):
        entries.append(("Upcoming", reverse("ietf.meeting.views.upcoming")))
        entries.append(("Pending", reverse("ietf.meeting.views.interim_pending")))
        if has_role(request.user, "Secretariat"):
            entries.append(("Announce", reverse("ietf.meeting.views.interim_announce")))
    return entries

def send_interim_change_notice(request, meeting):
    """Sends an email notifying changes to a previously scheduled / announced meeting"""
    group = meeting.session_set.first().group
    form = InterimAnnounceForm(get_announcement_initial(meeting, is_change=True))
    message = form.save(user=request.user)
    message.related_groups.add(group)
    send_mail_message(request, message)

# -------------------------------------------------
# View Functions
# -------------------------------------------------

def materials(request, num=None):
    meeting = get_meeting(num)
    begin_date = meeting.get_submission_start_date()
    cut_off_date = meeting.get_submission_cut_off_date()
    cor_cut_off_date = meeting.get_submission_correction_date()
    now = datetime.date.today()
    if settings.SERVER_MODE != 'production' and '_testoverride' in request.GET:
        pass
    elif now > cor_cut_off_date:
        if meeting.number.isdigit() and int(meeting.number) > 96:
            return redirect('ietf.meeting.views.proceedings', num=meeting.number)
        else:
            return render(request, "meeting/materials_upload_closed.html", {
                'meeting_num': meeting.number,
                'begin_date': begin_date,
                'cut_off_date': cut_off_date,
                'cor_cut_off_date': cor_cut_off_date
            })

    past_cutoff_date = datetime.date.today() > meeting.get_submission_correction_date()

    #sessions  = Session.objects.filter(meeting__number=meeting.number, timeslot__isnull=False)
    schedule = get_schedule(meeting, None)
    sessions  = ( Session.objects
        .filter(meeting__number=meeting.number, timeslotassignments__schedule=schedule)
        .select_related('meeting__agenda','status','group__state','group__parent', )
    )
    for session in sessions:
        session.past_cutoff_date = past_cutoff_date
    plenaries = sessions.filter(name__icontains='plenary')
    ietf      = sessions.filter(group__parent__type__slug = 'area').exclude(group__acronym='edu')
    irtf      = sessions.filter(group__parent__acronym = 'irtf')
    training  = sessions.filter(group__acronym__in=['edu','iaoc'], type_id__in=['session', 'other', ])
    iab       = sessions.filter(group__parent__acronym = 'iab')

    return render(request, "meeting/materials.html", {
        'meeting_num': meeting.number,
        'plenaries': plenaries,
        'ietf': ietf,
        'training': training,
        'irtf': irtf,
        'iab': iab,
        'cut_off_date': cut_off_date,
        'cor_cut_off_date': cor_cut_off_date,
        'submission_started': now > begin_date,
    })

def current_materials(request):
    meetings = Meeting.objects.exclude(number__startswith='interim-').order_by('-number')
    if meetings:
        return redirect(materials, meetings[0].number)
    else:
        raise Http404

@login_required
def materials_editable_groups(request, num=None):
    meeting = get_meeting(num)
    return render(request, "meeting/materials_editable_groups.html", {
        'meeting_num': meeting.number})

def ascii_alphanumeric(string):
    return re.match(r'^[a-zA-Z0-9]*$', string)

class SaveAsForm(forms.Form):
    savename = forms.CharField(max_length=16)

@role_required('Area Director','Secretariat')
def agenda_create(request, num=None, owner=None, name=None):
    meeting  = get_meeting(num)
    person   = get_person_by_email(owner)
    schedule = get_schedule_by_name(meeting, person, name)

    if schedule is None:
        # here we have to return some ajax to display an error.
        messages.error("Error: No meeting information for meeting %s owner %s schedule %s available" % (num, owner, name)) # pylint: disable=no-value-for-parameter
        return redirect(edit_agenda, num=num, owner=owner, name=name)

    # authorization was enforced by the @group_require decorator above.

    saveasform = SaveAsForm(request.POST)
    if not saveasform.is_valid():
        messages.info(request, "This name is not valid. Please choose another one.")
        return redirect(edit_agenda, num=num, owner=owner, name=name)

    savedname = saveasform.cleaned_data['savename']

    if not ascii_alphanumeric(savedname):
        messages.info(request, "This name contains illegal characters. Please choose another one.")
        return redirect(edit_agenda, num=num, owner=owner, name=name)

    # create the new schedule, and copy the assignments
    try:
        sched = meeting.schedule_set.get(name=savedname, owner=request.user.person)
        if sched:
            return redirect(edit_agenda, num=meeting.number, owner=sched.owner_email(), name=sched.name)
        else:
            messages.info(request, "Agenda creation failed. Please try again.")
            return redirect(edit_agenda, num=num, owner=owner, name=name)

    except Schedule.DoesNotExist:
        pass

    # must be done
    newschedule = Schedule(name=savedname,
                           owner=request.user.person,
                           meeting=meeting,
                           visible=False,
                           public=False)

    newschedule.save()
    if newschedule is None:
        return HttpResponse(status=500)

    # keep a mapping so that extendedfrom references can be chased.
    mapping = {};
    for ss in schedule.assignments.all():
        # hack to copy the object, creating a new one
        # just reset the key, and save it again.
        oldid = ss.pk
        ss.pk = None
        ss.schedule=newschedule
        ss.save()
        mapping[oldid] = ss.pk
        #print "Copying %u to %u" % (oldid, ss.pk)

    # now fix up any extendedfrom references to new set.
    for ss in newschedule.assignments.all():
        if ss.extendedfrom is not None:
            oldid = ss.extendedfrom.id
            newid = mapping[oldid]
            #print "Fixing %u to %u" % (oldid, newid)
            ss.extendedfrom = newschedule.assignments.get(pk = newid)
            ss.save()


    # now redirect to this new schedule.
    return redirect(edit_agenda, meeting.number, newschedule.owner_email(), newschedule.name)


@role_required('Secretariat')
@ensure_csrf_cookie
def edit_timeslots(request, num=None):

    meeting = get_meeting(num)
    timeslots = meeting.timeslot_set.exclude(location=None).select_related("location", "type")

    time_slices,date_slices,slots = meeting.build_timeslices()

    meeting_base_url = request.build_absolute_uri(meeting.base_url())
    site_base_url = request.build_absolute_uri('/')[:-1] # skip the trailing slash

    rooms = meeting.room_set.order_by("capacity")

    # this import locate here to break cyclic loop.
    from ietf.meeting.ajax import timeslot_roomsurl, AddRoomForm, timeslot_slotsurl, AddSlotForm
    roomsurl  = reverse(timeslot_roomsurl, args=[meeting.number])
    adddayurl = reverse(timeslot_slotsurl, args=[meeting.number])

    return render(request, "meeting/timeslot_edit.html",
                                         {"timeslots": timeslots,
                                          "meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "rooms":rooms,
                                          "addroom":  AddRoomForm(),
                                          "roomsurl": roomsurl,
                                          "addday":   AddSlotForm(),
                                          "adddayurl":adddayurl,
                                          "time_slices":time_slices,
                                          "slot_slices": slots,
                                          "date_slices":date_slices,
                                          "meeting":meeting,
                                          "hide_menu": True,
                                      })

class RoomForm(ModelForm):
    class Meta:
        model = Room
        exclude = ('meeting',)


##############################################################################
#@role_required('Area Director','Secretariat')
# disable the above security for now, check it below.
@ensure_csrf_cookie
def edit_agenda(request, num=None, owner=None, name=None):

    if request.method == 'POST':
        return agenda_create(request, num, owner, name)

    user     = request.user
    meeting  = get_meeting(num)
    person   = get_person_by_email(owner)
    if name is None:
        schedule = meeting.agenda
    else:
        schedule = get_schedule_by_name(meeting, person, name)
    if schedule is None:
        raise Http404("No meeting information for meeting %s owner %s schedule %s available" % (num, owner, name))

    meeting_base_url = request.build_absolute_uri(meeting.base_url())
    site_base_url = request.build_absolute_uri('/')[:-1] # skip the trailing slash

    rooms = meeting.room_set.filter(session_types__slug='session').distinct().order_by("capacity")
    saveas = SaveAsForm()
    saveasurl=reverse(edit_agenda,
                      args=[meeting.number, schedule.owner_email(), schedule.name])

    can_see, can_edit,secretariat = agenda_permissions(meeting, schedule, user)

    if not can_see:
        return render(request, "meeting/private_agenda.html",
                                             {"schedule":schedule,
                                              "meeting": meeting,
                                              "meeting_base_url":meeting_base_url,
                                              "hide_menu": True
                                          }, status=403, content_type="text/html")

    assignments = get_all_assignments_from_schedule(schedule)

    # get_modified_from needs the query set, not the list
    modified = get_modified_from_assignments(assignments)

    area_list = get_areas()
    wg_name_list = get_wg_name_list(assignments)
    wg_list = get_wg_list(wg_name_list)
    ads = find_ads_for_meeting(meeting)
    for ad in ads:
        # set the default to avoid needing extra arguments in templates
        # django 1.3+
        ad.default_hostscheme = site_base_url

    time_slices,date_slices = build_all_agenda_slices(meeting)

    return render(request, "meeting/landscape_edit.html",
                                         {"schedule":schedule,
                                          "saveas": saveas,
                                          "saveasurl": saveasurl,
                                          "meeting_base_url": meeting_base_url,
                                          "site_base_url": site_base_url,
                                          "rooms":rooms,
                                          "time_slices":time_slices,
                                          "date_slices":date_slices,
                                          "modified": modified,
                                          "meeting":meeting,
                                          "area_list": area_list,
                                          "area_directors" : ads,
                                          "wg_list": wg_list ,
                                          "assignments": assignments,
                                          "show_inline": set(["txt","htm","html"]),
                                          "hide_menu": True,
                                      })

##############################################################################
#  show the properties associated with an agenda (visible, public)
#
AgendaPropertiesForm = modelform_factory(Schedule, fields=('name','visible', 'public'))

@role_required('Area Director','Secretariat')
def edit_agenda_properties(request, num=None, owner=None, name=None):
    meeting  = get_meeting(num)
    person   = get_person_by_email(owner)
    schedule = get_schedule_by_name(meeting, person, name)
    if schedule is None:
        raise Http404("No meeting information for meeting %s owner %s schedule %s available" % (num, owner, name))

    cansee, canedit, secretariat = agenda_permissions(meeting, schedule, request.user)

    if not (canedit or has_role(request.user,'Secretariat')):
        return HttpResponseForbidden("You may not edit this agenda")
    else:
        if request.method == 'POST':
            form = AgendaPropertiesForm(instance=schedule,data=request.POST)
            if form.is_valid():
               form.save()
               return HttpResponseRedirect(reverse('ietf.meeting.views.list_agendas',kwargs={'num': num}))
        else: 
            form = AgendaPropertiesForm(instance=schedule)
        return render(request, "meeting/properties_edit.html",
                                             {"schedule":schedule,
                                              "form":form,
                                              "meeting":meeting,
                                          })

##############################################################################
# show list of agendas.
#

@role_required('Area Director','Secretariat')
def list_agendas(request, num=None ):

    meeting = get_meeting(num)
    user = request.user

    schedules = meeting.schedule_set
    if not has_role(user, 'Secretariat'):
        schedules = schedules.filter(visible = True) | schedules.filter(owner = user.person)

    schedules = schedules.order_by('owner', 'name')

    schedules = sorted(list(schedules),key=lambda x:not x.is_official)

    return render(request, "meeting/agenda_list.html",
                                         {"meeting":   meeting,
                                          "schedules": schedules,
                                          })

@ensure_csrf_cookie
def agenda(request, num=None, name=None, base=None, ext=None, owner=None, utc=""):
    base = base if base else 'agenda'
    ext = ext if ext else '.html'
    mimetype = {
        ".html":"text/html; charset=%s"%settings.DEFAULT_CHARSET,
        ".txt": "text/plain; charset=%s"%settings.DEFAULT_CHARSET,
        ".csv": "text/csv; charset=%s"%settings.DEFAULT_CHARSET,
    }

    meetings = get_meetings(num)

    # We do not have the appropriate data in the datatracker for IETF 64 and earlier.
    # So that we're not producing misleading pages...
    
    meeting = meetings.first()
    if not meetings.exists() or (meeting.number.isdigit() and meeting.number <= 64 and not meeting.agenda.assignments.exists()):
        if ext == '.html':
            return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s' % num )
        else:
            raise Http404

    if name is None:
        schedule = get_schedule(meeting, name)
    else:
        person   = get_person_by_email(owner)
        schedule = get_schedule_by_name(meeting, person, name)

    if schedule == None:
        base = base.replace("-utc", "")
        return render(request, "meeting/no-"+base+ext, {'meeting':meeting }, content_type=mimetype[ext])

    updated = meeting.updated()
    filtered_assignments = schedule.assignments.exclude(timeslot__type__in=['lead','offagenda'])
    filtered_assignments = preprocess_assignments_for_agenda(filtered_assignments, meeting)

    if ext == ".csv":
        return agenda_csv(schedule, filtered_assignments)

    # extract groups hierarchy, it's a little bit complicated because
    # we can be dealing with historic groups
    seen = set()
    groups = [a.session.historic_group for a in filtered_assignments
              if a.session
              and a.session.historic_group
              and a.session.historic_group.type_id in ('wg', 'rg', 'ag', 'iab')
              and a.session.historic_group.historic_parent]
    group_parents = []
    for g in groups:
        if g.historic_parent.acronym not in seen:
            group_parents.append(g.historic_parent)
            seen.add(g.historic_parent.acronym)

    seen = set()
    for p in group_parents:
        p.group_list = []
        for g in groups:
            if g.acronym not in seen and g.historic_parent.acronym == p.acronym:
                p.group_list.append(g)
                seen.add(g.acronym)

        p.group_list.sort(key=lambda g: g.acronym)

    return render(request, "meeting/"+base+ext, {
        "schedule": schedule,
        "filtered_assignments": filtered_assignments,
        "updated": updated,
        "group_parents": group_parents,
        "now": datetime.datetime.now(),
    }, content_type=mimetype[ext])

def agenda_csv(schedule, filtered_assignments):
    response = HttpResponse(content_type="text/csv; charset=%s"%settings.DEFAULT_CHARSET)
    writer = csv.writer(response, delimiter=',', quoting=csv.QUOTE_ALL)

    headings = ["Date", "Start", "End", "Session", "Room", "Area", "Acronym", "Type", "Description", "Session ID", "Agenda", "Slides"]

    def write_row(row):
        encoded_row = [v.encode('utf-8') if isinstance(v, unicode) else v for v in row]

        while len(encoded_row) < len(headings):
            encoded_row.append(None) # produce empty entries at the end as necessary

        writer.writerow(encoded_row)

    def agenda_field(item):
        agenda_doc = item.session.agenda()
        if agenda_doc:
            return "http://www.ietf.org/proceedings/{schedule.meeting.number}/agenda/{agenda.external_url}".format(schedule=schedule, agenda=agenda_doc)
        else:
            return ""

    def slides_field(item):
        return "|".join("http://www.ietf.org/proceedings/{schedule.meeting.number}/slides/{slide.external_url}".format(schedule=schedule, slide=slide) for slide in item.session.slides())

    write_row(headings)

    for item in filtered_assignments:
        row = []
        row.append(item.timeslot.time.strftime("%Y-%m-%d"))
        row.append(item.timeslot.time.strftime("%H%M"))
        row.append(item.timeslot.end_time().strftime("%H%M"))

        if item.timeslot.type_id == "break":
            row.append(item.timeslot.type.name)
            row.append(schedule.meeting.break_area)
            row.append("")
            row.append("")
            row.append("")
            row.append(item.timeslot.name)
            row.append("b{}".format(item.timeslot.pk))
        elif item.timeslot.type_id == "reg":
            row.append(item.timeslot.type.name)
            row.append(schedule.meeting.reg_area)
            row.append("")
            row.append("")
            row.append("")
            row.append(item.timeslot.name)
            row.append("r{}".format(item.timeslot.pk))
        elif item.timeslot.type_id == "other":
            row.append("None")
            row.append(item.timeslot.location.name if item.timeslot.location else "")
            row.append("")
            row.append(item.session.historic_group.acronym)
            row.append(item.session.historic_group.historic_parent.acronym.upper() if item.session.historic_group.historic_parent else "")
            row.append(item.session.name)
            row.append(item.session.pk)
        elif item.timeslot.type_id == "plenary":
            row.append(item.session.name)
            row.append(item.timeslot.location.name if item.timeslot.location else "")
            row.append("")
            row.append(item.session.historic_group.acronym if item.session.historic_group else "")
            row.append("")
            row.append(item.session.name)
            row.append(item.session.pk)
            row.append(agenda_field(item))
            row.append(slides_field(item))
        elif item.timeslot.type_id == "session":
            row.append(item.timeslot.name)
            row.append(item.timeslot.location.name if item.timeslot.location else "")
            row.append(item.session.historic_group.historic_parent.acronym.upper() if item.session.historic_group.historic_parent else "")
            row.append(item.session.historic_group.acronym if item.session.historic_group else "")
            row.append("BOF" if item.session.historic_group.state_id in ("bof", "bof-conc") else item.session.historic_group.type.name)
            row.append(item.session.historic_group.name if item.session.historic_group else "")
            row.append(item.session.pk)
            row.append(agenda_field(item))
            row.append(slides_field(item))

        if len(row) > 3:
            write_row(row)

    return response

@role_required('Area Director','Secretariat','IAB')
def agenda_by_room(request, num=None, name=None, owner=None):
    meeting = get_meeting(num) 
    if name is None:
        schedule = get_schedule(meeting)
    else:
        person   = get_person_by_email(owner)
        schedule = get_schedule_by_name(meeting, person, name)
    ss_by_day = OrderedDict()
    for day in schedule.assignments.dates('timeslot__time','day'):
        ss_by_day[day]=[]
    for ss in schedule.assignments.order_by('timeslot__location__functional_name','timeslot__location__name','timeslot__time'):
        day = ss.timeslot.time.date()
        ss_by_day[day].append(ss)
    return render(request,"meeting/agenda_by_room.html",{"meeting":meeting,"schedule":schedule,"ss_by_day":ss_by_day})

@role_required('Area Director','Secretariat','IAB')
def agenda_by_type(request, num=None, type=None, name=None, owner=None):
    meeting = get_meeting(num) 
    if name is None:
        schedule = get_schedule(meeting)
    else:
        person   = get_person_by_email(owner)
        schedule = get_schedule_by_name(meeting, person, name)
    assignments = schedule.assignments.order_by('session__type__slug','timeslot__time','session__group__acronym')
    if type:
        assignments = assignments.filter(session__type__slug=type)
    return render(request,"meeting/agenda_by_type.html",{"meeting":meeting,"schedule":schedule,"assignments":assignments})

@role_required('Area Director','Secretariat','IAB')
def agenda_by_type_ics(request,num=None,type=None):
    meeting = get_meeting(num) 
    schedule = get_schedule(meeting)
    assignments = schedule.assignments.order_by('session__type__slug','timeslot__time')
    if type:
        assignments = assignments.filter(session__type__slug=type)
    updated = meeting.updated()
    return render(request,"meeting/agenda.ics",{"schedule":schedule,"updated":updated,"assignments":assignments},content_type="text/calendar")

def session_document(request, num, acronym, type="agenda"):
    d = Document.objects.filter(type=type, session__meeting__number=num)
    if acronym == "plenaryt":
        d = d.filter(session__name__icontains="technical", session__slots__type="plenary")
    elif acronym == "plenaryw":
        d = d.filter(session__name__icontains="admin", session__slots__type="plenary")
    else:
        d = d.filter(session__group__acronym=acronym)

    if d:
        doc = d[0]
        html5_preamble = "<!doctype html><html lang=en><head><meta charset=utf-8><title>%s</title></head><body>"
        html5_postamble = "</body></html>"
        content, path = read_session_file(type, num, doc)
        _, ext = os.path.splitext(path)
        ext = ext.lstrip(".").lower()

        if not content:
            content = "Could not read %s file '%s'" % (type, path)
            return HttpResponse(content, content_type="text/plain; charset=%s"%settings.DEFAULT_CHARSET)

        if ext == "txt":
            return HttpResponse(content, content_type="text/plain; charset=%s"%settings.DEFAULT_CHARSET)
        elif ext == "pdf":
            return HttpResponse(content, content_type="application/pdf")
        elif ext in ["html", "htm"]:
            content=re.sub("(\r\n|\r)", "\n", content)
            d = PyQuery(content)
            d("head title").empty()
            d("head title").append(str(doc))
            d('meta[http-equiv]').remove()
            content = "<!doctype html>" + str(d)
        else:
            content = "<p>Unrecognized %s file '%s'</p>" % (type, doc.external_url)
            content = (html5_preamble % doc) + content + html5_postamble

        return HttpResponse(content)

    raise Http404("No %s for the %s session of IETF %s is available" % (type, acronym, num))

def session_agenda(request, num, session):
    return session_document(request, num, acronym=session, type='agenda')

def session_minutes(request, num, session):
    return session_document(request, num, acronym=session, type='minutes')

def session_draft_list(num, session):
    try:
        agendas = Document.objects.filter(type="agenda",
                                         session__meeting__number=num,
                                         session__group__acronym=session,
                                         states=State.objects.get(type="agenda", slug="active")).distinct()
    except Document.DoesNotExist:
        raise Http404

    drafts = set()
    for agenda in agendas:
        content, _ = read_agenda_file(num, agenda)
        if content:
            drafts.update(re.findall('(draft-[-a-z0-9]*)', content))

    result = []
    for draft in drafts:
        try:
            if re.search('-[0-9]{2}$', draft):
                doc_name = draft
            else:
                doc = Document.objects.get(name=draft)
                doc_name = draft + "-" + doc.rev

            if doc_name not in result:
                result.append(doc_name)
        except Document.DoesNotExist:
            pass

    return sorted(result)

def session_draft_tarfile(request, num, session):
    drafts = session_draft_list(num, session);

    response = HttpResponse(content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename=%s-drafts.tgz'%(session)
    tarstream = tarfile.open('','w:gz',response)
    mfh, mfn = mkstemp()
    os.close(mfh)
    manifest = open(mfn, "w")

    for doc_name in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, doc_name + ".pdf")

        if not os.path.exists(pdf_path):
            convert_draft_to_pdf(doc_name)

        if os.path.exists(pdf_path):
            try:
                tarstream.add(pdf_path, str(doc_name + ".pdf"))
                manifest.write("Included:  "+pdf_path+"\n")
            except Exception, e:
                manifest.write(("Failed (%s): "%e)+pdf_path+"\n")
        else:
            manifest.write("Not found: "+pdf_path+"\n")

    manifest.close()
    tarstream.add(mfn, "manifest.txt")
    tarstream.close()
    os.unlink(mfn)
    return response

def session_draft_pdf(request, num, session):
    drafts = session_draft_list(num, session);
    curr_page = 1
    pmh, pmn = mkstemp()
    os.close(pmh)
    pdfmarks = open(pmn, "w")
    pdf_list = ""

    for draft in drafts:
        pdf_path = os.path.join(settings.INTERNET_DRAFT_PDF_PATH, draft + ".pdf")
        if not os.path.exists(pdf_path):
            convert_draft_to_pdf(draft)

        if os.path.exists(pdf_path):
            pages = pdf_pages(pdf_path)
            pdfmarks.write("[/Page "+str(curr_page)+" /View [/XYZ 0 792 1.0] /Title (" + draft + ") /OUT pdfmark\n")
            pdf_list = pdf_list + " " + pdf_path
            curr_page = curr_page + pages

    pdfmarks.close()
    pdfh, pdfn = mkstemp()
    os.close(pdfh)
    pipe("gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=" + pdfn + " " + pdf_list + " " + pmn)

    pdf = open(pdfn,"r")
    pdf_contents = pdf.read()
    pdf.close()

    os.unlink(pmn)
    os.unlink(pdfn)
    return HttpResponse(pdf_contents, content_type="application/pdf")

def week_view(request, num=None, name=None, owner=None):
    meeting = get_meeting(num)

    if name is None:
        schedule = get_schedule(meeting)
    else:
        person   = get_person_by_email(owner)
        schedule = get_schedule_by_name(meeting, person, name)

    if not schedule:
        raise Http404

    filtered_assignments = schedule.assignments.exclude(timeslot__type__in=['lead','offagenda'])
    filtered_assignments = preprocess_assignments_for_agenda(filtered_assignments, meeting)
    
    items = []
    for a in filtered_assignments:
        # we don't HTML escape any of these as the week-view code is using createTextNode
        item = {
            "key": str(a.timeslot.pk),
            "day": a.timeslot.time.strftime("%w"),
            "time": a.timeslot.time.strftime("%H%M") + "-" + a.timeslot.end_time().strftime("%H%M"),
            "duration": a.timeslot.duration.seconds,
            "time_id": a.timeslot.time.strftime("%m%d%H%M"),
            "dayname": "{weekday}, {month} {day_of_month}, {year}".format(
                weekday=a.timeslot.time.strftime("%A").upper(),
                month=a.timeslot.time.strftime("%B"),
                day_of_month=a.timeslot.time.strftime("%d").lstrip("0"),
                year=a.timeslot.time.strftime("%Y"),
            ),
            "type": a.timeslot.type.name
        }

        if a.session:
            if a.session.historic_group:
                item["group"] = a.session.historic_group.acronym

            if a.session.name:
                item["name"] = a.session.name
            elif a.timeslot.type_id == "break":
                item["name"] = a.timeslot.name
                item["area"] = a.timeslot.type_id
                item["group"] = a.timeslot.type_id
            elif a.session.historic_group:
                item["name"] = a.session.historic_group.name
                if a.session.historic_group.state_id == "bof":
                    item["name"] += " BOF"

                item["state"] = a.session.historic_group.state.name
                if a.session.historic_group.historic_parent:
                    item["area"] = a.session.historic_group.historic_parent.acronym

            if a.timeslot.show_location:
                item["room"] = a.timeslot.get_location()

            if a.session and a.session.agenda():
                item["agenda"] = a.session.agenda().get_absolute_url()

        items.append(item)

    return render(request, "meeting/week-view.html", {
        "items": json.dumps(items),
    })

@role_required('Area Director','Secretariat','IAB')
def room_view(request, num=None, name=None, owner=None):
    meeting = get_meeting(num)

    rooms = meeting.room_set.order_by('functional_name','name')
    if not rooms.exists():
        return HttpResponse("No rooms defined yet")

    if name is None:
        schedule = get_schedule(meeting)
    else:
        person   = get_person_by_email(owner)
        schedule = get_schedule_by_name(meeting, person, name)

    assignments = schedule.assignments.all()
    unavailable = meeting.timeslot_set.filter(type__slug='unavail')
    if not (assignments.exists() or unavailable.exists()):
        return HttpResponse("No sessions/timeslots available yet")

    earliest = None
    latest = None

    if assignments:
        earliest = assignments.aggregate(Min('timeslot__time'))['timeslot__time__min']
        latest =  assignments.aggregate(Max('timeslot__time'))['timeslot__time__max']
        
    if unavailable:
        earliest_unavailable = unavailable.aggregate(Min('time'))['time__min']
        if not earliest or ( earliest_unavailable and earliest_unavailable < earliest ):
            earliest = earliest_unavailable
        latest_unavailable = unavailable.aggregate(Max('time'))['time__max']
        if not latest or ( latest_unavailable and latest_unavailable > latest ):
            latest = latest_unavailable

    if not (earliest and latest):
        raise Http404

    base_time = earliest
    base_day = datetime.datetime(base_time.year,base_time.month,base_time.day)

    day = base_day
    days = []
    while day <= latest :
        days.append(day)
        day += datetime.timedelta(days=1)

    unavailable = list(unavailable)
    for t in unavailable:
        t.delta_from_beginning = (t.time - base_time).total_seconds()
        t.day = (t.time-base_day).days

    assignments = list(assignments)
    for ss in assignments:
        ss.delta_from_beginning = (ss.timeslot.time - base_time).total_seconds()
        ss.day = (ss.timeslot.time-base_day).days

    template = "meeting/room-view.html"
    return render(request, template,{"meeting":meeting,"schedule":schedule,"unavailable":unavailable,"assignments":assignments,"rooms":rooms,"days":days})

def ical_agenda(request, num=None, name=None, ext=None):
    meeting = get_meeting(num)
    schedule = get_schedule(meeting, name)
    updated = meeting.updated()

    if schedule is None:
        raise Http404

    q = request.META.get('QUERY_STRING','') or ""
    filter = set(urllib.unquote(q).lower().split(','))
    include = [ i for i in filter if not (i.startswith('-') or i.startswith('~')) ]
    include_types = set(["plenary","other"])
    exclude = []

    # Process the special flags.
    #   "-wgname" will remove a working group from the output.
    #   "~Type" will add that type to the output.
    #   "-~Type" will remove that type from the output
    # Current types are:
    #   Session, Other (default on), Break, Plenary (default on)
    # Non-Working Group "wg names" include:
    #   edu, ietf, tools, iesg, iab

    for item in filter:
        if len(item) > 2 and item[0] == '-' and item[1] == '~':
            include_types -= set([item[2:]])
        elif len(item) > 1 and item[0] == '-':
            exclude.append(item[1:])
        elif len(item) > 1 and item[0] == '~':
            include_types |= set([item[1:]])

    assignments = schedule.assignments.exclude(timeslot__type__in=['lead','offagenda'])
    assignments = preprocess_assignments_for_agenda(assignments, meeting)

    assignments = [a for a in assignments if
                   (a.timeslot.type_id in include_types
                    or (a.session.historic_group and a.session.historic_group.acronym in include)
                    or (a.session.historic_group and a.session.historic_group.historic_parent and a.session.historic_group.historic_parent.acronym in include))
                   and (not a.session.historic_group or a.session.historic_group.acronym not in exclude)]

    return render(request, "meeting/agenda.ics", {
        "schedule": schedule,
        "assignments": assignments,
        "updated": updated
    }, content_type="text/calendar")

@cache_page(15 * 60)
def json_agenda(request, num=None ):
    meeting = get_meeting(num)

    sessions = []
    locations = set()
    parent_acronyms = set()
    assignments = meeting.agenda.assignments.exclude(session__type__in=['lead','offagenda','break','reg'])
    # Update the assignments with historic information, i.e., valid at the
    # time of the meeting
    assignments = preprocess_assignments_for_agenda(assignments, meeting)
    for asgn in assignments:
        sessdict = dict()
        sessdict['objtype'] = 'session'
        sessdict['id'] = asgn.pk
        sessdict['is_bof'] = False
        if asgn.session.historic_group:
            sessdict['group'] = {
                    "acronym": asgn.session.historic_group.acronym,
                    "name": asgn.session.historic_group.name,
                    "type": asgn.session.historic_group.type_id,
                    "state": asgn.session.historic_group.state_id,
                }
            if asgn.session.historic_group.is_bof():
                sessdict['is_bof'] = True
        if asgn.session.historic_group.type_id in ['wg','rg', 'ag',] or asgn.session.historic_group.acronym in ['iesg',]:
            sessdict['group']['parent'] = asgn.session.historic_group.historic_parent.acronym
            parent_acronyms.add(asgn.session.historic_group.historic_parent.acronym)
        if asgn.session.name:
            sessdict['name'] = asgn.session.name
        elif asgn.session.short:
            sessdict['name'] = asgn.session.short
        else:
            sessdict['name'] = asgn.session.historic_group.name
        sessdict['start'] = asgn.timeslot.utc_start_time().strftime("%Y-%m-%dT%H:%M:%SZ")
        sessdict['duration'] = str(asgn.timeslot.duration)
        sessdict['location'] = asgn.room_name
        if asgn.timeslot.location:      # Some socials have an assignment but no location
            locations.add(asgn.timeslot.location)
        if asgn.session.agenda():
            sessdict['agenda'] = asgn.session.agenda().href()

        if asgn.session.minutes():
            sessdict['minutes'] = asgn.session.minutes().href()
        if asgn.session.slides():
            # Deprecated 19 May 2017, remove after ietf 100;
            sessdict['slides'] = []
            for slides in asgn.session.slides():
                sessdict['slides'].append('/api/v1/doc/document/%s/'%slides.name)
            # New alternative
            sessdict['presentations'] = []
            presentations = SessionPresentation.objects.filter(session=asgn.session, document__type__slug='slides')
            for pres in presentations:
                sessdict['presentations'].append(
                    {
                        'name':     pres.document.name,
                        'title':    pres.document.title,
                        'order':    pres.order,
                        'rev':      pres.rev,
                        'resource_uri': '/api/v1/meeting/sessionpresentation/%s/'%pres.id,
                    })
        sessdict['session_res_uri'] = '/api/v1/meeting/session/%s/'%asgn.session.id
        sessdict['session_id'] = asgn.session.id
        modified = asgn.session.modified
        for doc in asgn.session.materials.all():
            rev_docevent = doc.latest_event(NewRevisionDocEvent,'new_revision')
            modified = max(modified, (rev_docevent and rev_docevent.time) or modified)
        sessdict['modified'] = modified
        sessions.append(sessdict)

    rooms = []
    for room in locations:
        roomdict = dict()
        roomdict['id'] = room.pk
        roomdict['objtype'] = 'location'
        roomdict['name'] = room.name
        if room.floorplan:
            roomdict['level_name'] = room.floorplan.name
            roomdict['level_sort'] = room.floorplan.order
        if room.x1 is not None:
            roomdict['x'] = (room.x1+room.x2)/2.0
            roomdict['y'] = (room.y1+room.y2)/2.0
        roomdict['modified'] = room.time
        if room.floorplan and room.floorplan.image:
            roomdict['map'] = room.floorplan.image.url
            roomdict['modified'] = max(room.time,room.floorplan.time)
        rooms.append(roomdict)

    parents = []
    for parent in Group.objects.filter(acronym__in=parent_acronyms):
        parentdict = dict()
        parentdict['id'] = parent.pk
        parentdict['objtype'] = 'parent'
        parentdict['name'] = parent.acronym
        parentdict['description'] = parent.name
        parentdict['modified'] = parent.time
        parents.append(parentdict)

    meetinfo = []
    meetinfo.extend(sessions)
    meetinfo.extend(rooms)
    meetinfo.extend(parents)
    meetinfo.sort(key=lambda x: x['modified'],reverse=True)
    last_modified = meetinfo and meetinfo[0]['modified']

    tz = pytz.timezone(settings.PRODUCTION_TIMEZONE)

    for obj in meetinfo:
        obj['modified'] = tz.localize(obj['modified']).astimezone(pytz.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    data = {"%s"%num: meetinfo}

    response = HttpResponse(json.dumps(data, indent=2, sort_keys=True), content_type='application/json;charset=%s'%settings.DEFAULT_CHARSET)
    if last_modified:
        last_modified = tz.localize(last_modified).astimezone(pytz.utc)
        response['Last-Modified'] = format_date_time(timegm(last_modified.timetuple()))
    return response

def meeting_requests(request, num=None):
    meeting = get_meeting(num)
    sessions = Session.objects.filter(meeting__number=meeting.number, type__slug='session', group__parent__isnull = False).exclude(requested_by=0).order_by("group__parent__acronym","status__slug","group__acronym")

    groups_not_meeting = Group.objects.filter(state='Active',type__in=['wg','rg','ag','bof']).exclude(acronym__in = [session.group.acronym for session in sessions]).order_by("parent__acronym","acronym")

    return render(request, "meeting/requests.html",
        {"meeting": meeting, "sessions":sessions,
         "groups_not_meeting": groups_not_meeting})

def get_sessions(num, acronym):
    meeting = get_meeting(num=num,type_in=None)
    sessions = Session.objects.filter(meeting=meeting,group__acronym=acronym,type__in=['session','plenary','other'])

    if not sessions:
        sessions = Session.objects.filter(meeting=meeting,short=acronym,type__in=['session','plenary','other']) 

    def sort_key(session):
        official_sessions = session.timeslotassignments.filter(schedule=session.meeting.agenda)
        if official_sessions:
            return official_sessions.first().timeslot.time
        else:
            return session.requested

    return sorted(sessions,key=sort_key)

def session_details(request, num, acronym ):
    meeting = get_meeting(num=num,type_in=None)
    sessions = get_sessions(num, acronym)

    if not sessions:
        raise Http404

    for session in sessions:

        session.type_counter = Counter()
        ss = session.timeslotassignments.filter(schedule=meeting.agenda).order_by('timeslot__time')
        if ss:
            session.time = ', '.join(x.timeslot.time.strftime("%A %b-%d-%Y %H%M") for x in ss) 
            if session.status.slug == 'canceled':
                session.time += " CANCELLED"
        elif session.meeting.type_id=='interim':
            session.time = session.meeting.date.strftime("%A %b-%d-%Y")
            if session.status.slug == 'canceled':
                session.time += " CANCELLED"
        else:
            session.time = session.status.name

        session.filtered_artifacts = session.sessionpresentation_set.filter(document__type__slug__in=['agenda','minutes','bluesheets'])
        session.filtered_slides    = session.sessionpresentation_set.filter(document__type__slug='slides').order_by('order')
        session.filtered_drafts    = session.sessionpresentation_set.filter(document__type__slug='draft')
        # TODO FIXME Deleted materials shouldn't be in the sessionpresentation_set
        for qs in [session.filtered_artifacts,session.filtered_slides,session.filtered_drafts]:
            qs = [p for p in qs if p.document.get_state_slug(p.document.type_id)!='deleted']
            session.type_counter.update([p.document.type.slug for p in qs])

    can_manage = can_manage_materials(request.user, Group.objects.get(acronym=acronym))

    return render(request, "meeting/session_details.html",
                  { 'sessions':sessions ,
                    'meeting' :meeting ,
                    'acronym' :acronym,
                    'can_manage_materials' : can_manage,
                  })

class SessionDraftsForm(forms.Form):
    drafts = SearchableDocumentsField(required=False)

    def __init__(self, *args, **kwargs):
        self.already_linked = kwargs.pop('already_linked')
        super(self.__class__, self).__init__(*args, **kwargs)

    def clean(self):
        selected = self.cleaned_data['drafts']
        problems = set(selected).intersection(set(self.already_linked)) 
        if problems:
           raise forms.ValidationError("Already linked: %s" % ', '.join([d.name for d in problems]))
        return self.cleaned_data

def add_session_drafts(request, session_id, num):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)
    if not session.can_manage_materials(request.user):
        raise Http404
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        raise Http404

    already_linked = [sp.document for sp in session.sessionpresentation_set.filter(document__type_id='draft')]

    session_number = None
    sessions = get_sessions(session.meeting.number,session.group.acronym)
    if len(sessions) > 1:
       session_number = 1 + sessions.index(session)

    if request.method == 'POST':
        form = SessionDraftsForm(request.POST,already_linked=already_linked)
        if form.is_valid():
            for draft in form.cleaned_data['drafts']:
                session.sessionpresentation_set.create(document=draft,rev=None)
                c = DocEvent(type="added_comment", doc=draft, rev=draft.rev, by=request.user.person)
                c.desc = "Added to session: %s" % session
                c.save()
            return redirect('ietf.meeting.views.session_details', num=session.meeting.number, acronym=session.group.acronym)
    else:
        form = SessionDraftsForm(already_linked=already_linked)

    return render(request, "meeting/add_session_drafts.html",
                  { 'session': session,
                    'session_number': session_number,
                    'already_linked': session.sessionpresentation_set.filter(document__type_id='draft'),
                    'form': form,
                  })

class UploadBlueSheetForm(forms.Form):
    file = forms.FileField(label='Bluesheet scan to upload')

    def clean_file(self):
        file = self.cleaned_data['file']
        validate_mime_type(file, settings.MEETING_VALID_BLUESHEET_MIME_TYPES)
        validate_file_extension(file, settings.MEETING_VALID_BLUESHEET_EXTENSIONS)
        return file

@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair')
def upload_session_bluesheets(request, session_id, num):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)

    if session.meeting.type.slug == 'ietf' and not has_role(request.user, 'Secretariat'):
        return HttpResponseForbidden('Restricted to role Secretariat')
        
    session_number = None
    sessions = get_sessions(session.meeting.number,session.group.acronym)
    if len(sessions) > 1:
       session_number = 1 + sessions.index(session)

    bluesheet_sp = session.sessionpresentation_set.filter(document__type='bluesheets').first()
    
    if request.method == 'POST':
        form = UploadBlueSheetForm(request.POST,request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            _, ext = os.path.splitext(file.name)
            if bluesheet_sp:
                doc = bluesheet_sp.document
                doc.rev = '%02d' % (int(doc.rev)+1)
                bluesheet_sp.rev = doc.rev
                bluesheet_sp.save()
            else:
                ota = session.official_timeslotassignment()
                sess_time = ota and ota.timeslot.time
                if session.meeting.type_id=='ietf':
                    name = 'bluesheets-%s-%s-%s' % (session.meeting.number, 
                                                    session.group.acronym, 
                                                    sess_time.strftime("%Y%m%d%H%M"))
                    title = 'Bluesheets IETF%s: %s : %s' % (session.meeting.number, 
                                                            session.group.acronym, 
                                                            sess_time.strftime("%a %H:%M"))
                else:
                    name = 'bluesheets-%s-%s' % (session.meeting.number, sess_time.strftime("%Y%m%d%H%M"))
                    title = 'Bluesheets %s: %s' % (session.meeting.number, sess_time.strftime("%a %H:%M"))
                doc = Document.objects.create(
                          name = name,
                          type_id = 'bluesheets',
                          title = title,
                          group = session.group,
                          rev = '00',
                      )
                doc.states.add(State.objects.get(type_id='bluesheets',slug='active'))
                doc.docalias_set.create(name=doc.name)
                session.sessionpresentation_set.create(document=doc,rev='00')
            filename = '%s-%s%s'% ( doc.name, doc.rev, ext)
            doc.external_url = filename
            e = NewRevisionDocEvent.objects.create(doc=doc, rev=doc.rev, by=request.user.person, type='new_revision', desc='New revision available: %s'%doc.rev)
            doc.save_with_history([e])
            handle_upload_file(file, filename, session.meeting, 'bluesheets')
            return redirect('ietf.meeting.views.session_details',num=num,acronym=session.group.acronym)
    else: 
        form = UploadBlueSheetForm()

    return render(request, "meeting/upload_session_bluesheets.html", 
                  {'session': session,
                   'session_number': session_number,
                   'bluesheet_sp' : bluesheet_sp,
                   'form': form,
                  })


# FIXME: This form validation code (based on the secretariat upload code) only looks at filename extensions
#        It should look at the contents of the files instead. 
class UploadMinutesForm(forms.Form):
    file = forms.FileField(label='Minutes file to upload. Note that you can only upload minutes in txt, html, or pdf formats.')
    apply_to_all = forms.BooleanField(label='Apply to all group sessions at this meeting',initial=True,required=False)

    def __init__(self, show_apply_to_all_checkbox, *args, **kwargs):
        super(UploadMinutesForm, self).__init__(*args, **kwargs)
        if not show_apply_to_all_checkbox:
            self.fields.pop('apply_to_all')

    def clean_file(self):
        file = self.cleaned_data['file']
        validate_file_size(file)
        ext = validate_file_extension(file, settings.MEETING_VALID_MINUTES_EXTENSIONS)
        mime_type, encoding = validate_mime_type(file, settings.MEETING_VALID_MINUTES_MIME_TYPES)
        if ext in ['.html', '.htm'] or mime_type in ['text/html', ]:
            validate_no_html_frame(file)
        return file

def upload_session_minutes(request, session_id, num):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)

    if not session.can_manage_materials(request.user):
        return HttpResponseForbidden("You don't have permission to upload minutes for this session.")
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        return HttpResponseForbidden("The materials cutoff for this session has passed. Contact the secretariat for further action.")

    session_number = None
    sessions = get_sessions(session.meeting.number,session.group.acronym)
    show_apply_to_all_checkbox = len(sessions) > 1 if session.type_id == 'session' else False
    if len(sessions) > 1:
       session_number = 1 + sessions.index(session)

    minutes_sp = session.sessionpresentation_set.filter(document__type='minutes').first()
    
    if request.method == 'POST':
        form = UploadMinutesForm(show_apply_to_all_checkbox,request.POST,request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            _, ext = os.path.splitext(file.name)
            apply_to_all = session.type_id == 'session'
            if show_apply_to_all_checkbox:
                apply_to_all = form.cleaned_data['apply_to_all']
            if minutes_sp:
                doc = minutes_sp.document
                doc.rev = '%02d' % (int(doc.rev)+1)
                minutes_sp.rev = doc.rev
                minutes_sp.save()
            else:
                ota = session.official_timeslotassignment()
                sess_time = ota and ota.timeslot.time
                if session.meeting.type_id=='ietf':
                    name = 'minutes-%s-%s' % (session.meeting.number, 
                                                 session.group.acronym) 
                    title = 'Minutes IETF%s: %s' % (session.meeting.number, 
                                                         session.group.acronym) 
                    if not apply_to_all:
                        name += '-%s' % (sess_time.strftime("%Y%m%d%H%M"),)
                        title += ': %s' % (sess_time.strftime("%a %H:%M"),)
                else:
                    name = 'minutes-%s-%s' % (session.meeting.number, sess_time.strftime("%Y%m%d%H%M"))
                    title = 'Minutes %s: %s' % (session.meeting.number, sess_time.strftime("%a %H:%M"))
                doc = Document.objects.create(
                          name = name,
                          type_id = 'minutes',
                          title = title,
                          group = session.group,
                          rev = '00',
                      )
                doc.states.add(State.objects.get(type_id='minutes',slug='active'))
                doc.docalias_set.create(name=doc.name)
                session.sessionpresentation_set.create(document=doc,rev='00')
            if apply_to_all:
                for other_session in sessions:
                    if other_session != session:
                        other_session.sessionpresentation_set.filter(document__type='minutes').delete()
                        other_session.sessionpresentation_set.create(document=doc,rev=doc.rev)
            filename = '%s-%s%s'% ( doc.name, doc.rev, ext)
            doc.external_url = filename
            e = NewRevisionDocEvent.objects.create(doc=doc, time=doc.time, by=request.user.person, type='new_revision', desc='New revision available: %s'%doc.rev, rev=doc.rev)
            doc.save_with_history([e])
            # The way this function builds the filename it will never trigger the file delete in handle_file_upload.
            handle_upload_file(file, filename, session.meeting, 'minutes')
            return redirect('ietf.meeting.views.session_details',num=num,acronym=session.group.acronym)
    else: 
        form = UploadMinutesForm(show_apply_to_all_checkbox)

    return render(request, "meeting/upload_session_minutes.html", 
                  {'session': session,
                   'session_number': session_number,
                   'minutes_sp' : minutes_sp,
                   'form': form,
                  })


# FIXME: This form validation code (based on the secretariat upload code) only looks at filename extensions
#        It should look at the contents of the files instead. 
class UploadAgendaForm(forms.Form):
    file = forms.FileField(label='Agenda file to upload. Note that you can only upload agendas in txt or html formats.')
    apply_to_all = forms.BooleanField(label='Apply to all group sessions at this meeting',initial=True,required=False)

    def __init__(self, show_apply_to_all_checkbox, *args, **kwargs):
        super(UploadAgendaForm, self).__init__(*args, **kwargs)
        if not show_apply_to_all_checkbox:
            self.fields.pop('apply_to_all')

    def clean_file(self):
        file = self.cleaned_data['file']
        validate_file_size(file)
        ext = validate_file_extension(file, settings.MEETING_VALID_AGENDA_EXTENSIONS)
        mime_type, encoding = validate_mime_type(file, settings.MEETING_VALID_AGENDA_MIME_TYPES)
        if ext in ['.html', '.htm'] or mime_type in ['text/html', ]:
            validate_no_html_frame(file)
        return file

def upload_session_agenda(request, session_id, num):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)

    if not session.can_manage_materials(request.user):
        return HttpResponseForbidden("You don't have permission to upload an agenda for this session.")
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        return HttpResponseForbidden("The materials cutoff for this session has passed. Contact the secretariat for further action.")

    session_number = None
    sessions = get_sessions(session.meeting.number,session.group.acronym)
    show_apply_to_all_checkbox = len(sessions) > 1 if session.type_id == 'session' else False
    if len(sessions) > 1:
       session_number = 1 + sessions.index(session)

    agenda_sp = session.sessionpresentation_set.filter(document__type='agenda').first()
    
    if request.method == 'POST':
        form = UploadAgendaForm(show_apply_to_all_checkbox,request.POST,request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            _, ext = os.path.splitext(file.name)
            apply_to_all = session.type_id == 'session'
            if show_apply_to_all_checkbox:
                apply_to_all = form.cleaned_data['apply_to_all']
            if agenda_sp:
                doc = agenda_sp.document
                doc.rev = '%02d' % (int(doc.rev)+1)
                agenda_sp.rev = doc.rev
                agenda_sp.save()
            else:
                ota = session.official_timeslotassignment()
                sess_time = ota and ota.timeslot.time
                if session.meeting.type_id=='ietf':
                    name = 'agenda-%s-%s' % (session.meeting.number, 
                                                 session.group.acronym) 
                    title = 'Agenda IETF%s: %s' % (session.meeting.number, 
                                                         session.group.acronym) 
                    if not apply_to_all:
                        name += '-%s' % (session.docname_token(),)
                        if sess_time:
                            title += ': %s' % (sess_time.strftime("%a %H:%M"),)
                else:
                    name = 'agenda-%s-%s' % (session.meeting.number, session.docname_token())
                    title = 'Agenda %s' % (session.meeting.number, )
                    if sess_time:
                        title += ': %s' % (sess_time.strftime("%a %H:%M"),)
                if Document.objects.filter(name=name).exists():
                    doc = Document.objects.get(name=name)
                    doc.rev = '%02d' % (int(doc.rev)+1)
                else:
                    doc = Document.objects.create(
                              name = name,
                              type_id = 'agenda',
                              title = title,
                              group = session.group,
                              rev = '00',
                          )
                    doc.docalias_set.create(name=doc.name)
                doc.states.add(State.objects.get(type_id='agenda',slug='active'))
            if session.sessionpresentation_set.filter(document=doc).exists():
                sp = session.sessionpresentation_set.get(document=doc)
                sp.rev = doc.rev
                sp.save()
            else:
                session.sessionpresentation_set.create(document=doc,rev=doc.rev)
            if apply_to_all:
                for other_session in sessions:
                    if other_session != session:
                        other_session.sessionpresentation_set.filter(document__type='agenda').delete()
                        other_session.sessionpresentation_set.create(document=doc,rev=doc.rev)
            filename = '%s-%s%s'% ( doc.name, doc.rev, ext)
            doc.external_url = filename
            e = NewRevisionDocEvent.objects.create(doc=doc,time=doc.time,by=request.user.person,type='new_revision',desc='New revision available: %s'%doc.rev,rev=doc.rev)
            doc.save_with_history([e])
            # The way this function builds the filename it will never trigger the file delete in handle_file_upload.
            handle_upload_file(file, filename, session.meeting, 'agenda')
            return redirect('ietf.meeting.views.session_details',num=num,acronym=session.group.acronym)
    else: 
        form = UploadAgendaForm(show_apply_to_all_checkbox, initial={'apply_to_all':session.type_id=='session'})

    return render(request, "meeting/upload_session_agenda.html", 
                  {'session': session,
                   'session_number': session_number,
                   'agenda_sp' : agenda_sp,
                   'form': form,
                  })


# FIXME: This form validation code (based on the secretariat upload code) only looks at filename extensions
#        It should look at the contents of the files instead. 
class UploadSlidesForm(forms.Form):
    title = forms.CharField(max_length=255)
    file = forms.FileField(label='Slides file to upload.')
    apply_to_all = forms.BooleanField(label='Apply to all group sessions at this meeting',initial=False,required=False)

    def __init__(self, show_apply_to_all_checkbox, *args, **kwargs):
        super(UploadSlidesForm, self).__init__(*args, **kwargs)
        if not show_apply_to_all_checkbox:
            self.fields.pop('apply_to_all')

    def clean_file(self):
        file = self.cleaned_data['file']
        validate_file_size(file)
        validate_file_extension(file, settings.MEETING_VALID_SLIDES_EXTENSIONS)
        return file

def upload_session_slides(request, session_id, num, name):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)
    if not session.can_manage_materials(request.user):
        return HttpResponseForbidden("You don't have permission to upload slides for this session.")
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        return HttpResponseForbidden("The materials cutoff for this session has passed. Contact the secretariat for further action.")

    session_number = None
    sessions = get_sessions(session.meeting.number,session.group.acronym)
    show_apply_to_all_checkbox = len(sessions) > 1 if session.type_id == 'session' else False
    if len(sessions) > 1:
       session_number = 1 + sessions.index(session)

    slides = None
    slides_sp = None
    if name:
        slides = Document.objects.filter(name=name).first()
        if not (slides and slides.type_id=='slides'):
            raise Http404
        slides_sp = session.sessionpresentation_set.filter(document=slides).first()
    
    if request.method == 'POST':
        form = UploadSlidesForm(show_apply_to_all_checkbox,request.POST,request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            _, ext = os.path.splitext(file.name)
            apply_to_all = session.type_id == 'session'
            if show_apply_to_all_checkbox:
                apply_to_all = form.cleaned_data['apply_to_all']
            if slides_sp:
                doc = slides_sp.document
                doc.rev = '%02d' % (int(doc.rev)+1)
                doc.title = form.cleaned_data['title']
                slides_sp.rev = doc.rev
                slides_sp.save()
            else:
                title = form.cleaned_data['title']
                if session.meeting.type_id=='ietf':
                    name = 'slides-%s-%s' % (session.meeting.number, 
                                             session.group.acronym) 
                    if not apply_to_all:
                        name += '-%s' % (session.docname_token(),)
                else:
                    name = 'slides-%s-%s' % (session.meeting.number, session.docname_token())
                name = name + '-' + slugify(title)
                if Document.objects.filter(name=name).exists():
                   doc = Document.objects.get(name=name)
                   doc.rev = '%02d' % (int(doc.rev)+1)
                   doc.title = form.cleaned_data['title']
                else:
                    doc = Document.objects.create(
                              name = name,
                              type_id = 'slides',
                              title = title,
                              group = session.group,
                              rev = '00',
                          )
                    doc.docalias_set.create(name=doc.name)
                doc.states.add(State.objects.get(type_id='slides',slug='active'))
                doc.states.add(State.objects.get(type_id='reuse_policy',slug='single'))
            if session.sessionpresentation_set.filter(document=doc).exists():
                sp = session.sessionpresentation_set.get(document=doc)
                sp.rev = doc.rev
                sp.save()
            else:
                max_order = session.sessionpresentation_set.filter(document__type='slides').aggregate(Max('order'))['order__max'] or 0
                session.sessionpresentation_set.create(document=doc,rev=doc.rev,order=max_order+1)
            if apply_to_all:
                for other_session in sessions:
                    if other_session != session and not other_session.sessionpresentation_set.filter(document=doc).exists():
                        max_order = other_session.sessionpresentation_set.filter(document__type='slides').aggregate(Max('order'))['order__max'] or 0
                        other_session.sessionpresentation_set.create(document=doc,rev=doc.rev,order=max_order+1)
            filename = '%s-%s%s'% ( doc.name, doc.rev, ext)
            doc.external_url = filename
            e = NewRevisionDocEvent.objects.create(doc=doc,time=doc.time,by=request.user.person,type='new_revision',desc='New revision available: %s'%doc.rev,rev=doc.rev)
            doc.save_with_history([e])
            # The way this function builds the filename it will never trigger the file delete in handle_file_upload.
            handle_upload_file(file, filename, session.meeting, 'slides')
            post_process(doc)
            return redirect('ietf.meeting.views.session_details',num=num,acronym=session.group.acronym)
    else: 
        initial = {}
        if slides:
            initial = {'title':slides.title}
        form = UploadSlidesForm(show_apply_to_all_checkbox, initial=initial)

    return render(request, "meeting/upload_session_slides.html", 
                  {'session': session,
                   'session_number': session_number,
                   'slides_sp' : slides_sp,
                   'form': form,
                  })

def remove_sessionpresentation(request, session_id, num, name):
    sp = get_object_or_404(SessionPresentation,session_id=session_id,document__name=name)
    session = sp.session
    if not session.can_manage_materials(request.user):
        return HttpResponseForbidden("You don't have permission to manage materials for this session.")
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        return HttpResponseForbidden("The materials cutoff for this session has passed. Contact the secretariat for further action.")
    if request.method == 'POST':
        session.sessionpresentation_set.filter(pk=sp.pk).delete()
        c = DocEvent(type="added_comment", doc=sp.document, rev=sp.document.rev, by=request.user.person)
        c.desc = "Removed from session: %s" % (session)
        c.save()
        return redirect('ietf.meeting.views.session_details', num=session.meeting.number, acronym=session.group.acronym)

    return render(request,'meeting/remove_sessionpresentation.html', {'sp': sp })

def set_slide_order(request, session_id, num, name):
    # num is redundant, but we're dragging it along an artifact of where we are in the current URL structure
    session = get_object_or_404(Session,pk=session_id)
    if not Document.objects.filter(type_id='slides',name=name).exists():
        raise Http404
    if not session.can_manage_materials(request.user):
        return HttpResponseForbidden("You don't have permission to upload slides for this session.")
    if session.is_material_submission_cutoff() and not has_role(request.user, "Secretariat"):
        return HttpResponseForbidden("The materials cutoff for this session has passed. Contact the secretariat for further action.")

    if request.method != 'POST' or not request.POST:
        return HttpResponse(json.dumps({ 'success' : False, 'error' : 'No data submitted or not POST' }),content_type='application/json')
    order_str = request.POST.get('order', None)
    try:
        order = int(order_str)
    except ValueError:
        return HttpResponse(json.dumps({ 'success' : False, 'error' : 'Supplied order is not valid' }),content_type='application/json')
    if order <=0 or order > 32767 :
        return HttpResponse(json.dumps({ 'success' : False, 'error' : 'Supplied order is not valid' }),content_type='application/json')
    
    sp = session.sessionpresentation_set.get(document__name = name)
    sp.order = order
    sp.save()

    return HttpResponse(json.dumps({'success':True}),content_type='application/json')

@role_required('Secretariat')
def make_schedule_official(request, num, owner, name):

    meeting  = get_meeting(num)
    person   = get_person_by_email(owner)
    schedule = get_schedule_by_name(meeting, person, name)

    if schedule is None:
        raise Http404

    if request.method == 'POST':
        if not (schedule.public and schedule.visible):
            schedule.public = True
            schedule.visible = True
            schedule.save()
        meeting.agenda = schedule
        meeting.save()
        return HttpResponseRedirect(reverse('ietf.meeting.views.list_agendas',kwargs={'num':num}))

    if not schedule.public:
        messages.warning(request,"This schedule will be made public as it is made official.")

    if not schedule.visible:
        messages.warning(request,"This schedule will be made visible as it is made official.")

    return render(request, "meeting/make_schedule_official.html",
                  { 'schedule' : schedule,
                    'meeting' : meeting,
                  }
                 )
    

@role_required('Secretariat','Area Director')
def delete_schedule(request, num, owner, name):

    meeting  = get_meeting(num)
    person   = get_person_by_email(owner)
    schedule = get_schedule_by_name(meeting, person, name)

    if schedule.name=='Empty-Schedule':
        return HttpResponseForbidden('You may not delete the default empty schedule')

    if schedule == meeting.agenda:
        return HttpResponseForbidden('You may not delete the official agenda for %s'%meeting)

    if not ( has_role(request.user, 'Secretariat') or person.user == request.user ):
        return HttpResponseForbidden("You may not delete other user's schedules")

    if request.method == 'POST':
        schedule.delete()
        return HttpResponseRedirect(reverse('ietf.meeting.views.list_agendas',kwargs={'num':num}))

    return render(request, "meeting/delete_schedule.html",
                  { 'schedule' : schedule,
                    'meeting' : meeting,
                  }
                 )
  
# -------------------------------------------------
# Interim Views
# -------------------------------------------------


def ajax_get_utc(request):
    '''Ajax view that takes arguments time, timezone, date and returns UTC data'''
    time = request.GET.get('time')
    timezone = request.GET.get('timezone')
    date = request.GET.get('date')
    time_re = re.compile(r'^\d{2}:\d{2}$')
    # validate input
    if not time_re.match(time) or not date:
        return HttpResponse(json.dumps({'error': True}),
                            content_type='application/json')
    hour, minute = time.split(':')
    if not (int(hour) <= 23 and int(minute) <= 59):
        return HttpResponse(json.dumps({'error': True}),
                            content_type='application/json')
    year, month, day = date.split('-')
    dt = datetime.datetime(int(year), int(month), int(day), int(hour), int(minute))
    tz = pytz.timezone(timezone)
    aware_dt = tz.localize(dt, is_dst=None)
    utc_dt = aware_dt.astimezone(pytz.utc)
    utc = utc_dt.strftime('%H:%M')
    # calculate utc day offset
    naive_utc_dt = utc_dt.replace(tzinfo=None)
    utc_day_offset = (naive_utc_dt.date() - dt.date()).days
    html = "<span>{utc} UTC</span>".format(utc=utc)
    if utc_day_offset != 0:
        html = html + "<span class='day-offset'> {0:+d} Day</span>".format(utc_day_offset)
    context_data = {'timezone': timezone, 
                    'time': time, 
                    'utc': utc, 
                    'utc_day_offset': utc_day_offset,
                    'html': html}
    return HttpResponse(json.dumps(context_data),
                        content_type='application/json')


@role_required('Secretariat',)
def interim_announce(request):
    '''View which shows interim meeting requests awaiting announcement'''
    meetings = Meeting.objects.filter(type='interim', session__status='scheda').distinct()
    menu_entries = get_menu_entries(request)
    selected_menu_entry = 'announce'

    return render(request, "meeting/interim_announce.html", {
        'menu_entries': menu_entries,
        'selected_menu_entry': selected_menu_entry,
        'meetings': meetings})


@role_required('Secretariat',)
def interim_send_announcement(request, number):
    '''View for sending the announcement of a new interim meeting'''
    meeting = get_object_or_404(Meeting, number=number)
    group = meeting.session_set.first().group

    if request.method == 'POST':
        form = InterimAnnounceForm(request.POST,
                                   initial=get_announcement_initial(meeting))
        if form.is_valid():
            message = form.save(user=request.user)
            message.related_groups.add(group)
            meeting.session_set.update(status_id='sched')
            send_mail_message(request, message)
            messages.success(request, 'Interim meeting announcement sent')
            return redirect(interim_announce)

    form = InterimAnnounceForm(initial=get_announcement_initial(meeting))

    return render(request, "meeting/interim_send_announcement.html", {
        'meeting': meeting,
        'form': form})


@role_required('Secretariat',)
def interim_skip_announcement(request, number):
    '''View to change status of interim meeting to Scheduled without
    first announcing.  Only applicable to IRTF groups.
    '''
    meeting = get_object_or_404(Meeting, number=number)

    if request.method == 'POST':
        meeting.session_set.update(status_id='sched')
        messages.success(request, 'Interim meeting scheduled.  No announcement sent.')
        return redirect(interim_announce)

    return render(request, "meeting/interim_skip_announce.html", {
        'meeting': meeting})


@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair',
               'RG Chair')
def interim_pending(request):
    '''View which shows interim meeting requests pending approval'''
    meetings = Meeting.objects.filter(type='interim', session__status='apprw').distinct().order_by('date')
    menu_entries = get_menu_entries(request)
    selected_menu_entry = 'pending'

    meetings = [m for m in meetings if can_view_interim_request(
        m, request.user)]
    for meeting in meetings:
        if can_approve_interim_request(meeting, request.user):
            meeting.can_approve = True

    return render(request, "meeting/interim_pending.html", {
        'menu_entries': menu_entries,
        'selected_menu_entry': selected_menu_entry,
        'meetings': meetings})


@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair',
               'RG Chair')
def interim_request(request):
    '''View for requesting an interim meeting'''
    SessionFormset = inlineformset_factory(
        Meeting,
        Session,
        form=InterimSessionModelForm,
        formset=InterimSessionInlineFormSet,
        can_delete=False, extra=2)

    if request.method == 'POST':
        form = InterimMeetingModelForm(request, data=request.POST)
        formset = SessionFormset(instance=Meeting(), data=request.POST)
        if form.is_valid() and formset.is_valid():
            group = form.cleaned_data.get('group')
            is_approved = form.cleaned_data.get('approved', False)
            is_virtual = form.is_virtual()
            meeting_type = form.cleaned_data.get('meeting_type')

            # pre create meeting
            if meeting_type in ('single', 'multi-day'):
                meeting = form.save(date=get_earliest_session_date(formset))

                # need to use curry here to pass custom variable to form init
                SessionFormset.form.__init__ = curry(
                    InterimSessionModelForm.__init__,
                    user=request.user,
                    group=group,
                    is_approved_or_virtual=(is_approved or is_virtual))
                formset = SessionFormset(instance=meeting, data=request.POST)
                formset.is_valid()
                formset.save()
                sessions_post_save(formset)

                if not (is_approved or is_virtual):
                    send_interim_approval_request(meetings=[meeting])
                elif not has_role(request.user, 'Secretariat'):
                    send_interim_announcement_request(meeting=meeting)

            # series require special handling, each session gets it's own
            # meeting object we won't see this on edit because series are
            # subsequently dealt with individually
            elif meeting_type == 'series':
                series = []
                SessionFormset.form.__init__ = curry(
                    InterimSessionModelForm.__init__,
                    user=request.user,
                    group=group,
                    is_approved_or_virtual=(is_approved or is_virtual))
                formset = SessionFormset(instance=Meeting(), data=request.POST)
                formset.is_valid()  # re-validate
                for session_form in formset.forms:
                    if not session_form.has_changed():
                        continue
                    # create meeting
                    form = InterimMeetingModelForm(request, data=request.POST)
                    form.is_valid()
                    meeting = form.save(date=session_form.cleaned_data['date'])
                    # create save session
                    session = session_form.save(commit=False)
                    session.meeting = meeting
                    session.save()
                    series.append(meeting)
                    sessions_post_save([session_form])

                if not (is_approved or is_virtual):
                    send_interim_approval_request(meetings=series)
                elif not has_role(request.user, 'Secretariat'):
                    send_interim_announcement_request(meeting=meeting)

            messages.success(request, 'Interim meeting request submitted')
            return redirect(upcoming)

    else:
        initial = {'meeting_type': 'single', 'group': request.GET.get('group', '')}
        form = InterimMeetingModelForm(request=request, 
                                       initial=initial)
        formset = SessionFormset()

    return render(request, "meeting/interim_request.html", {
        "form": form,
        "formset": formset})


@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair',
               'RG Chair')
def interim_request_cancel(request, number):
    '''View for cancelling an interim meeting request'''
    meeting = get_object_or_404(Meeting, number=number)
    group = meeting.session_set.first().group
    if not can_view_interim_request(meeting, request.user):
        return HttpResponseForbidden("You do not have permissions to cancel this meeting request")

    if request.method == 'POST':
        form = InterimCancelForm(request.POST)
        if form.is_valid():
            if 'comments' in form.changed_data:
                meeting.session_set.update(agenda_note=form.cleaned_data.get('comments'))
            if meeting.session_set.first().status.slug == 'sched':
                meeting.session_set.update(status_id='canceled')
                send_interim_cancellation_notice(meeting)
            else:
                meeting.session_set.update(status_id='canceledpa')
            messages.success(request, 'Interim meeting cancelled')
            return redirect(upcoming)
    else:
        form = InterimCancelForm(initial={'group': group.acronym, 'date': meeting.date})

    return render(request, "meeting/interim_request_cancel.html", {
        "form": form,
        "meeting": meeting})


@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair',
               'RG Chair')
def interim_request_details(request, number):
    '''View details of an interim meeting reqeust'''
    meeting = get_object_or_404(Meeting, number=number)
    sessions = meeting.session_set.all()
    can_edit = can_edit_interim_request(meeting, request.user)
    can_approve = can_approve_interim_request(meeting, request.user)

    if request.method == 'POST':
        if request.POST.get('approve') and can_approve_interim_request(meeting, request.user):
            meeting.session_set.update(status_id='scheda')
            messages.success(request, 'Interim meeting approved')
            if has_role(request.user, 'Secretariat'):
                return redirect(interim_send_announcement, number=number)
            else:
                send_interim_announcement_request(meeting)
                return redirect(interim_pending)
        if request.POST.get('disapprove') and can_approve_interim_request(meeting, request.user):
            meeting.session_set.update(status_id='disappr')
            messages.success(request, 'Interim meeting disapproved')
            return redirect(interim_pending)

    return render(request, "meeting/interim_request_details.html", {
        "meeting": meeting,
        "sessions": sessions,
        "can_edit": can_edit,
        "can_approve": can_approve})


@role_required('Area Director', 'Secretariat', 'IRTF Chair', 'WG Chair',
               'RG Chair')
def interim_request_edit(request, number):
    '''Edit details of an interim meeting reqeust'''
    meeting = get_object_or_404(Meeting, number=number)
    if not can_edit_interim_request(meeting, request.user):
        return HttpResponseForbidden("You do not have permissions to edit this meeting request")

    SessionFormset = inlineformset_factory(
        Meeting,
        Session,
        form=InterimSessionModelForm,
        can_delete=False,
        extra=1)

    if request.method == 'POST':
        form = InterimMeetingModelForm(request=request, instance=meeting,
                                       data=request.POST)
        group = Group.objects.get(pk=form.data['group'])
        is_approved = is_meeting_approved(meeting)

        SessionFormset.form.__init__ = curry(
            InterimSessionModelForm.__init__,
            user=request.user,
            group=group,
            is_approved_or_virtual=is_approved)

        formset = SessionFormset(instance=meeting, data=request.POST)

        if form.is_valid() and formset.is_valid():
            meeting = form.save(date=get_earliest_session_date(formset))
            formset.save()
            sessions_post_save(formset)

            message = 'Interim meeting request saved'
            if (form.has_changed() or formset.has_changed()) and meeting.session_set.filter(status='sched'):
                send_interim_change_notice(request, meeting)
                message = message + ' and change announcement sent'
            messages.success(request, message)
            return redirect(interim_request_details, number=number)

    else:
        form = InterimMeetingModelForm(request=request, instance=meeting)
        formset = SessionFormset(instance=meeting)

    return render(request, "meeting/interim_request_edit.html", {
        "meeting": meeting,
        "form": form,
        "formset": formset})

@cache_page(60*60)
def past(request):
    '''List of past meetings'''
    today = datetime.datetime.today()
    meetings = ( Meeting.objects.filter(date__lte=today)
            .exclude(session__status__in=('apprw', 'scheda', 'canceledpa'))
            .order_by('-date')
            .select_related('type')
            .prefetch_related('session_set__status','session_set__group',)
        )

    # extract groups hierarchy for display filter
    seen = set()
    groups = [m.session_set.first().group for m
              in meetings.filter(type='interim')]
    group_parents = []
    for g in groups:
        if g.parent.acronym not in seen:
            group_parents.append(g.parent)
            seen.add(g.parent.acronym)

    seen = set()
    for p in group_parents:
        p.group_list = []
        for g in groups:
            if g.acronym not in seen and g.parent == p:
                p.group_list.append(g)
                seen.add(g.acronym)

        p.group_list.sort(key=lambda g: g.acronym)

    return render(request, 'meeting/past.html', {
                  'meetings': meetings,
                  'group_parents': group_parents})

def upcoming(request):
    '''List of upcoming meetings'''
    today = datetime.datetime.today()
    meetings = Meeting.objects.filter(date__gte=today).exclude(
        session__status__in=('apprw', 'scheda', 'canceledpa')).order_by('date')

    # extract groups hierarchy for display filter
    seen = set()
    groups = [m.session_set.first().group for m
              in meetings.filter(type='interim')]
    group_parents = []
    for g in groups:
        if g.parent.acronym not in seen:
            group_parents.append(g.parent)
            seen.add(g.parent.acronym)

    seen = set()
    for p in group_parents:
        p.group_list = []
        for g in groups:
            if g.acronym not in seen and g.parent == p:
                p.group_list.append(g)
                seen.add(g.acronym)

        p.group_list.sort(key=lambda g: g.acronym)

    # add menu entries
    menu_entries = get_menu_entries(request)
    selected_menu_entry = 'upcoming'

    # add menu actions
    actions = []
    if can_request_interim_meeting(request.user):
        actions.append(('Request new interim meeting',
                        reverse('ietf.meeting.views.interim_request')))
    actions.append(('Download as .ics',
                    reverse('ietf.meeting.views.upcoming_ical')))

    return render(request, 'meeting/upcoming.html', {
                  'meetings': meetings,
                  'menu_actions': actions,
                  'menu_entries': menu_entries,
                  'selected_menu_entry': selected_menu_entry,
                  'group_parents': group_parents})


def upcoming_ical(request):
    '''Return Upcoming meetings in iCalendar file'''
    filters = request.GET.getlist('filters')
    today = datetime.datetime.today()
    meetings = Meeting.objects.filter(date__gte=today).exclude(
        session__status__in=('apprw', 'schedpa')).order_by('date')

    assignments = []
    for meeting in meetings:
        items = meeting.agenda.assignments.order_by(
            'session__type__slug', 'timeslot__time')
        assignments.extend(items)

    # apply filters
    if filters:
        assignments = [a for a in assignments if
                       a.session.group and (
                           a.session.group.acronym in filters or (
                               a.session.group.parent and a.session.group.parent.acronym in filters
                           )
                       ) ]
    # gather vtimezones
    vtimezones = set()
    for meeting in meetings:
        if meeting.vtimezone():
            vtimezones.add(meeting.vtimezone())
    vtimezones = ''.join(vtimezones)

    # icalendar response file should have '\r\n' line endings per RFC5545
    response = render_to_string('meeting/upcoming.ics', {
        'vtimezones': vtimezones,
        'assignments': assignments})
    response = re.sub("\r(?!\n)|(?<!\r)\n", "\r\n", response)

    response = HttpResponse(response, content_type='text/calendar')
    response['Content-Disposition'] = 'attachment; filename="upcoming.ics"'
    return response
    

def floor_plan(request, num=None, floor=None, ):
    meeting = get_meetings(num).first()
    schedule = meeting.agenda
    floors = FloorPlan.objects.filter(meeting=meeting).order_by('order')
    if floor:
        floors = [ f for f in floors if xslugify(f.name) == floor ]
    return render(request, 'meeting/floor-plan.html', {
            "schedule": schedule,
            "number": num,
            "floors": floors,
        })

def proceedings(request, num=None):

    meeting = get_meeting(num)

    if meeting.number <= 64 or not meeting.agenda.assignments.exists():
            return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s' % num )

    begin_date = meeting.get_submission_start_date()
    cut_off_date = meeting.get_submission_cut_off_date()
    cor_cut_off_date = meeting.get_submission_correction_date()
    now = datetime.date.today()

    schedule = get_schedule(meeting, None)
    sessions  = Session.objects.filter(meeting__number=meeting.number).filter(Q(timeslotassignments__schedule=schedule)|Q(status='notmeet')).select_related().order_by('-status_id')
    plenaries = sessions.filter(name__icontains='plenary').exclude(status='notmeet')
    ietf      = sessions.filter(group__parent__type__slug = 'area').exclude(group__acronym='edu')
    irtf      = sessions.filter(group__parent__acronym = 'irtf')
    training  = sessions.filter(group__acronym__in=['edu','iaoc'], type_id__in=['session', 'other', ]).exclude(status='notmeet')
    iab       = sessions.filter(group__parent__acronym = 'iab').exclude(status='notmeet')

    cache_version = Document.objects.filter(session__meeting__number=meeting.number).aggregate(Max('time'))["time__max"]
    return render(request, "meeting/proceedings.html", {
        'meeting': meeting,
        'plenaries': plenaries, 'ietf': ietf, 'training': training, 'irtf': irtf, 'iab': iab,
        'cut_off_date': cut_off_date,
        'cor_cut_off_date': cor_cut_off_date,
        'submission_started': now > begin_date,
        'cache_version': cache_version,
    })

@role_required('Secretariat')
def finalize_proceedings(request, num=None):

    meeting = get_meeting(num)

    if meeting.number <= 64 or not meeting.agenda.assignments.exists() or meeting.proceedings_final:
        raise Http404

    if request.method=='POST':
        finalize(meeting)
        return HttpResponseRedirect(reverse('ietf.meeting.views.proceedings',kwargs={'num':meeting.number}))
    
    return render(request, "meeting/finalize.html", {'meeting':meeting,})

def proceedings_acknowledgements(request, num=None):
    '''Display Acknowledgements for meeting'''
    meeting = get_meeting(num)
    if not num.isdigit():
        raise Http404
    if int(meeting.number) < settings.NEW_PROCEEDINGS_START:
        return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s/acknowledgement.html' % num )
    return render(request, "meeting/proceedings_acknowledgements.html", {
        'meeting': meeting,
    })

def proceedings_attendees(request, num=None):
    '''Display list of meeting attendees'''
    meeting = get_meeting(num)
    if not num.isdigit():
        raise Http404
    if int(meeting.number) < settings.NEW_PROCEEDINGS_START:
        return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s/attendees.html' % num )
    overview_template = '/meeting/proceedings/%s/attendees.html' % meeting.number
    try:
        template = render_to_string(overview_template, {})
    except TemplateDoesNotExist:
        raise Http404
    return render(request, "meeting/proceedings_attendees.html", {
        'meeting': meeting,
        'template': template,
    })

def proceedings_overview(request, num=None):
    '''Display Overview for given meeting'''
    meeting = get_meeting(num)
    if not num.isdigit():
        raise Http404
    if int(meeting.number) < settings.NEW_PROCEEDINGS_START:
        return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s/overview.html' % num )
    overview_template = '/meeting/proceedings/%s/overview.rst' % meeting.number
    try:
        template = render_to_string(overview_template, {})
    except TemplateDoesNotExist:
        raise Http404
    return render(request, "meeting/proceedings_overview.html", {
        'meeting': meeting,
        'template': template,
    })

@cache_page( 60 * 60 )
def proceedings_progress_report(request, num=None):
    '''Display Progress Report (stats since last meeting)'''
    meeting = get_meeting(num)
    if not num.isdigit():
        raise Http404
    if int(meeting.number) < settings.NEW_PROCEEDINGS_START:
        return HttpResponseRedirect( 'https://www.ietf.org/proceedings/%s/progress-report.html' % num )
    sdate = meeting.previous_meeting().date
    edate = meeting.date
    context = get_progress_stats(sdate,edate)
    context['meeting'] = meeting
    return render(request, "meeting/proceedings_progress_report.html", context)
    
class OldUploadRedirect(RedirectView):
    def get_redirect_url(self, **kwargs):
        return reverse_lazy('ietf.meeting.views.session_details',kwargs=self.kwargs)

@csrf_exempt
def api_import_recordings(request, number):
    '''REST API to check for recording files and import'''
    if request.method == 'POST':
        meeting = get_meeting(number)
        import_audio_files(meeting)
        import_youtube_video_urls(meeting)
        return HttpResponse(status=201)
    else:
        return HttpResponse(status=405)


