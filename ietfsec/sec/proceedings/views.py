from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.core.urlresolvers import reverse
from django.db.models import Max
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.template import Context
from django.template.loader import get_template
from django.utils import simplejson
from django.db.models import Max,Count,get_model

from sec.core.models import Acronym
from sec.core.forms import GroupSelectForm
from sec.drafts.models import InternetDraft, Rfc
from sec.proceedings.models import *
from sec.utils.decorators import sec_only, check_permissions
from sec.utils.shortcuts import get_group_or_404, get_meeting_or_404, get_my_groups

from forms import *
from models import *

import datetime
import glob
import itertools
import os
import re
import shutil
import zipfile

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------
def build_choices(queryset):
    '''
    This function takes a queryset (or list of objects) and builds a list of tuples for use 
    as choices in a select widget.  First item is the object primary key, second is the object
    name, str(obj).
    '''
    choices = zip([ x.pk for x in queryset ],
                  [ str(x) for x in queryset ])
    return sorted(choices, key=lambda choices: choices[1])

def create_proceedings(meeting):
    '''
    This function creates the proceedings.html document.  It gets called anytime there is an
    update to the meeting or the slides for the meeting.
    
    NOTE:
    AS OF DEPLOYMENT (06-06-2011) THIS FUNCTION ONLY USED FOR INTERIM MEETINGS.
    So we check if the meeting is interim, if not we do nothing.  For now regular
    proceedings are being built by Priyanka's PHP app.
    
    If activating for regulary proceedings need to:
    - remove abort
    - change the proceedings_path
    - changes slides queryset
    - change minutes and agenda queries
    '''
    
    # abort if not interim
    if not is_interim_meeting(meeting):
        return
        
    # get all the objects we need for the template
    # meeting = get_meeting_or_404(meeting_id)
    year,month,day = parsedate(meeting.start_date)
    group_name = meeting.get_group_acronym()
    group = IETFWG.objects.get(group_acronym=meeting.group_acronym_id)
    area_group = AreaGroup.objects.get(group=group.group_acronym)
    area_name = area_group.area.area_acronym.name
    slides = meeting.interimslide_set.all().order_by('order_num')
    # drafts and rfcs are available from methods on group, but they aren't sorted
    drafts = InternetDraft.objects.filter(group=meeting.group_acronym_id,
                                                    status=1).order_by('start_date')
    rfcs = Rfc.objects.filter(group_acronym=meeting.get_group_acronym()).order_by('rfc_number')
    agenda_url = ''
    minutes_url = ''
    try:
        agenda = InterimAgenda.objects.get(meeting=meeting,group_acronym_id=group.pk)
        if os.path.exists(agenda.file_path):
            agenda_url = agenda.url
    except InterimAgenda.DoesNotExist:
        pass
    
    try:
        minutes = InterimMinute.objects.get(meeting=meeting,group_acronym_id=group.pk)
        if os.path.exists(minutes.file_path):
            minutes_url = minutes.url
    except InterimMinute.DoesNotExist:
        pass
    
    # the simplest way to display the charter is to place it in a <pre> block
    # however, because this forces a fixed-width font, different than the rest of
    # the document we modify the charter by adding replacing linefeeds with <br>'s
    charter = group.charter_text().replace('\n','<br>')
    
    # rather than return the response as in a typical view function we save it as the snapshot
    # proceedings.html
    response = render_to_response('proceedings/proceedings.html',{
        'agenda_url': agenda_url,
        'area_name': area_name,
        'charter': charter,
        'drafts': drafts,
        'group': group,
        'meeting':meeting,
        'minutes_url': minutes_url,
        'rfcs': rfcs,
        'slides': slides}
    )
    
    # save proceedings
    proceedings_path = meeting.get_proceedings_path()
    
    f = open(proceedings_path,'w')
    f.write(response.content)
    f.close()
    
    # save the meeting object, which will cause "updated" field to be current
    # reverted to legacy meeting table which does not have update field
    # meeting.save()
    
def find_index(slide_id, qs):
    '''
    This function looks up a slide in a queryset of slides,
    returning the index.
    '''
    for i in range(0,qs.count()):
        if str(qs[i].id) == slide_id:
            return i

def get_agenda(meeting,group):
    '''
    This function takes a meeting object (regular or interim) and a
    group object (regular or IRTF) and returns the associated agenda object.
    '''
    try:
        if is_interim_meeting(meeting):
            agenda = InterimAgenda.objects.get(meeting=meeting,group_acronym_id=group.pk)
        else:
            agenda = WgAgenda.objects.get(meeting=meeting,group_acronym_id=group.pk)
    except ObjectDoesNotExist:
        agenda = None
    return agenda

def get_materials_object(meeting_id,type,object_id):
    '''
    This function takes
    meeting_id: id of meeting
    type: string [agenda|minute|slide]
    object_id: the object id
    
    and returns the object instance
    '''
    interim = is_interim_meeting(meeting_id)

    if type == 'slide':
        if interim:
            obj = get_object_or_404(InterimSlide, id=object_id)
        else:
            obj = get_object_or_404(Slide, id=object_id)        
    
    elif type == 'agenda':
        if interim:
            obj = get_object_or_404(InterimAgenda, id=object_id)
        else:
            obj = get_object_or_404(WgAgenda, id=object_id)
    
    elif type == 'minute':
        if interim:
            obj = get_object_or_404(InterimMinute, id=object_id)
        else:
            obj = get_object_or_404(Minute, id=object_id)
        
    return obj
    
def get_minutes(meeting,group):
    '''
    This function takes a meeting object (regular or interim) and a
    group object (regular or IRTF) and returns the associated agenda object.
    '''
    try:
        if is_interim_meeting(meeting):
            minutes = InterimMinute.objects.get(meeting=meeting,group_acronym_id=group.pk)
        else:
            minutes = Minute.objects.get(meeting=meeting,group_acronym_id=group.pk)
    except ObjectDoesNotExist:
        minutes = None
    return minutes

def get_next_slide_num(meeting,group):
    '''
    This function takes a meeting object (regular or interim) and a group object and returns the
    next slide number to use for a newly added slide.
    '''
    # TODO candidate for method
    if is_interim_meeting(meeting):
        max_slide_num = InterimSlide.objects.filter(meeting=meeting,group_acronym_id=group.pk).aggregate(Max('slide_num'))['slide_num__max']
    else:
        max_slide_num = Slide.objects.filter(meeting=meeting,group_acronym_id=group.pk).aggregate(Max('slide_num'))['slide_num__max']
    
    if max_slide_num is None:
        slide_num = '0'
    else:
        slide_num = max_slide_num + 1
    return slide_num
    
def get_next_order_num(meeting,group):
    '''
    This function takes a meeting object (regular or interim) and a group object and returns the
    next slide order number to use for a newly added slide.
    '''
    # TODO candidate for wrapper
    if is_interim_meeting(meeting):
        max_order_num = InterimSlide.objects.filter(meeting=meeting,group_acronym_id=group.pk).aggregate(Max('order_num'))['order_num__max']
    else:
        max_order_num = Slide.objects.filter(meeting=meeting,group_acronym_id=group.pk).aggregate(Max('order_num'))['order_num__max']
    
    if max_order_num is None:
        order_num = '1'
    else:
        order_num = max_order_num + 1
    
    return order_num
                    
def get_slides(meeting,group):
    '''
    This function takes a meeting object (regular or interim) and a group object and returns a
    queryset of the assoicated slides.
    '''
    if is_interim_meeting(meeting):
        slides = InterimSlide.objects.filter(meeting=meeting,group_acronym_id=group.pk).order_by('order_num')
    else: 
        slides = Slide.objects.filter(meeting=meeting,group_acronym_id=group.pk).order_by('order_num')
    return slides

def handle_upload_file(file,filename,meeting,subdir): 
    '''
    This function takes a file object, a filename and a meeting object (can be either Meeting
    or InterimMeeting).  It saves the file to the appropriate directory, get_upload_root() + subdir.
    If the file is a zip file, it creates a new directory in 'slides', which is the basename of the
    zip file and unzips the file in the new directory.
    '''
    filename = filename.lower()
    base, extension = os.path.splitext(filename)
    
    if extension == '.zip':
        path = os.path.join(meeting.get_upload_root(),subdir,base)
        if not os.path.exists(path):
            os.mkdir(path)
    else:
        path = os.path.join(meeting.get_upload_root(),subdir)
        
    destination = open(os.path.join(path,filename), 'wb+')
    for chunk in file.chunks():
        destination.write(chunk)
    destination.close()

    # unzip zipfile
    if extension == '.zip':
        os.chdir(path)
        os.system('unzip %s' % filename)

def is_interim_meeting(meeting):
    '''
    This a general function which takes one of:
    - an integer representing the meeting number
    - a string representing the meeting number
    - an instance of one of two meeting classes: Meeting, InterimMeeting
    Returns True if the meeting is an Interim Meeting
    '''
    if isinstance(meeting,InterimMeeting):
        return True
    elif isinstance(meeting,Meeting):
        return False
    elif int(meeting) >= 200:
        return True
        
    return False
        
def log_activity(group_id,text,meeting_id,userid):
    '''
    Add a record to session_request_activites.  Based on legacy function
    input: group can be either IETFWG or IRTF
    '''
    record = WgProceedingsActivity(group_acronym_id=group_id,meeting_num=meeting_id,activity=text,act_by=userid)
    record.save()
    
def make_directories(meeting):
    '''
    This function takes a meeting object and creates the appropriate materials directories
    '''
    path = meeting.upload_root
    os.umask(0)
    if not os.path.exists(path):
        os.makedirs(path)
    os.mkdir(os.path.join(path,'slides'))
    os.mkdir(os.path.join(path,'agenda'))
    os.mkdir(os.path.join(path,'minutes'))
    os.mkdir(os.path.join(path,'id'))
    os.mkdir(os.path.join(path,'rfc'))
    
def parsedate(d):
    '''
    This function takes a date object and returns a tuple of year,month,day
    '''
    return (d.strftime('%Y'),d.strftime('%m'),d.strftime('%d'))
    
# --------------------------------------------------
# STANDARD VIEW FUNCTIONS
# --------------------------------------------------
@sec_only
def convert(request, meeting_id):
    '''
    Handles the PPT to HTML conversion download/upload process.

    Slides waiting in a list for conversion are listed and manual Upload/Download is

    performed
 

    **Templates:**

    * ``proceedings/convert.html``

    **Template Variables:**

    * meeting , proceeding, slide_info

    '''
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_id)

    #Get the file names in queue waiting for the conversion
    slide_list = Slide.objects.filter(meeting=meeting_id,in_q='1')

    return render_to_response('proceedings/convert.html', {
        'meeting': meeting,
        'proceeding': proceeding,
        'slide_list':slide_list},
        RequestContext(request, {}),
    )

@check_permissions
def delete_material(request,meeting_id,group_id,type,object_id):
    '''
    This view handles deleting material objects and files.  
    "type" argument must be a string [agenda|slide|minute]
    '''

    obj = get_materials_object(meeting_id,type,object_id)
    
    path = obj.file_path
    if os.path.exists(path):
        os.remove(path)
        
    '''
    TODO: special case for removing html directories
    # for now this isn't supported
    #if os.path.isdir(path):
    #   shutil.rmtree(path)
    # slide_type_id == 1 is a special type, indicates a direcory containing html docs
        # we need to get the directory name and remove it
        if obj.slide_type_id == 1:
            slide_dir = os.path.splitext(obj.filename)[0]
            path = os.path.join(settings.PROCEEDINGS_DIR,str(meeting_id),'slides',slide_dir)
    '''
    # log activity
    if type == 'agenda':
        text = "agenda was deleted"
    elif type == 'minute':
        text = "minutes was deleted"
    elif type == 'slide':
        text = "slide, '%s', was deleted" % obj.slide_name
    log_activity(group_id,text,meeting_id,request.person)

    obj.delete()
        
    messages.success(request,'The material was deleted successfully')
    url = reverse('proceedings_upload_unified', kwargs={'meeting_id':meeting_id,'group_id':obj.group_acronym_id})
    return HttpResponseRedirect(url)

@sec_only
def delete_interim_meeting(request, meeting_id):
    '''
    This view deletes the specified InterimMeeting and any material that has been
    uploaded for it.
    '''
    meeting = get_object_or_404(InterimMeeting, meeting_num=meeting_id)
    
    # delete directories
    path = meeting.get_upload_root()
    if os.path.exists(path):
        shutil.rmtree(path)
    
    meeting.delete()

    url = reverse('proceedings_interim', kwargs={'group_id':meeting.group_acronym_id})
    return HttpResponseRedirect(url)
    
@check_permissions
def edit_slide(request, meeting_id, group_id, slide_id):
    '''
    This view allows the user to edit the name of a slide.
    '''
    # we need to pass group to the template for the breadcrumbs
    group = get_group_or_404(group_id)
    slide = get_materials_object(meeting_id,'slide',slide_id)

    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('proceedings_upload_unified', kwargs={'meeting_id':slide.meeting.pk,'group_id':slide.group_acronym_id})
            return HttpResponseRedirect(url)
            
        form = EditSlideForm(request.POST, instance=slide) # A form bound to the POST data
        if form.is_valid(): 
            # log activity
            text = "Title of a slide was changed to '%s' from '%s'" % (form.cleaned_data['slide_name'],form.initial['slide_name']) 
            log_activity(group_id,text,meeting_id,request.person)
            
            form.save()
            
            # rebuild proceedings.html
            # create_proceedings(slide.meeting.pk)
            url = reverse('proceedings_upload_unified', kwargs={'meeting_id':slide.meeting.pk,'group_id':slide.group_acronym_id})
            return HttpResponseRedirect(url)
    else:
        form = EditSlideForm(instance=slide)
    
    return render_to_response('proceedings/edit_slide.html',{
        'group': group,
        'interim': is_interim_meeting(meeting_id),
        'meeting':slide.meeting,
        'slide':slide,
        'form':form},
        RequestContext(request, {}),
    )

def interim(request, group_id):
    '''
    This view presents the user with a list of interim meetings for the specified group.
    The user can select a meeting to manage or create a new interim meeting by entering
    a date.
    '''
    group_name = Acronym.objects.get(acronym_id=group_id).acronym
    group = get_object_or_404(IETFWG, group_acronym=group_id)
    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Back':
            url = reverse('proceedings_select_interim')
            return HttpResponseRedirect(url)
            
        form = InterimMeetingForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            start_date = form.cleaned_data['date']
            meeting=InterimMeeting()
            meeting.group_acronym_id = group_id
            meeting.start_date = start_date
            meeting.save()
            make_directories(meeting)
            messages.success(request, 'Meeting created')
            url = reverse('proceedings_interim', kwargs={'group_id':group_id})
            return HttpResponseRedirect(url)
    else:
        form = InterimMeetingForm(initial={'group_acronym_id':group_id}) # An unbound form
        
    meeting_list = InterimMeeting.objects.filter(group_acronym_id=group_id).order_by('start_date')
    return render_to_response('proceedings/interim_meeting.html',{
        'group_name': group_name,
        'group': group,
        'meeting_list':meeting_list,
        'form':form},
        RequestContext(request, {}),
    )
    
def main(request):
    '''
    List IETF Meetings.  If the user is Secratariat list includes all meetings otherwise
    show only those meetings which are not frozen and whose corrections submission date has
    not passed.

    **Templates:**

    * ``proceedings/list.html``

    **Template Variables:**

    * proceeding_list

    '''
    if request.user_is_secretariat:
        proceeding_list = Proceeding.objects.order_by('meeting_num')
    else:
        today = datetime.date.today()
        proceeding_list = Proceeding.objects.filter(frozen=0,c_sub_cut_off_date__gte=today).order_by('meeting_num')
    
    interim_meetings = []
    for group in get_my_groups(request):
        qs = InterimMeeting.objects.filter(group_acronym_id=group.pk)
        interim_meetings.extend(qs)
    
    return render_to_response('proceedings/main.html',{
        'proceeding_list': proceeding_list,
        'interim_meetings': interim_meetings},
        RequestContext(request,{}), 
    )
    
@sec_only
def modify(request,id):
    '''
    Handle status changes of Proceedings (Activate, Freeze)

    **Templates:**

    * none

    Redirects to view page on success.

    '''
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    if request.method == 'POST':
        #Handles the freeze request
        if request.POST.get('submit', '') == "Freeze":  
            proceeding.frozen=1
            proceeding.save()
            messages.success(request, 'Proceedings have been freezed successfully!')

        if request.POST.get('submit','') == "Activate":
            proceeding.frozen=0
            proceeding.save()
            messages.success(request, 'Proceedings have been activated successfully!')

        url = reverse('sec.proceedings.views.view', kwargs={'id':str(id)})
        return HttpResponseRedirect(url)
        
@check_permissions
def move_slide(request, meeting_id, group_id, slide_id, direction):
    '''
    This view will re-order slides.  In addition to meeting, group and slide IDs it takes
    a direction argument which is a string [up|down].
    '''
    if is_interim_meeting(meeting_id):
        slide = get_object_or_404(InterimSlide, id=slide_id)
    else:
        slide = get_object_or_404(Slide, id=slide_id)
    meeting_id = slide.meeting.meeting_num
    group_id = slide.group_acronym_id
    
    # get related slides
    # TODO this would make a good Slide model method
    if is_interim_meeting(meeting_id):
        qs = InterimSlide.objects.filter(meeting=meeting_id,group_acronym_id=group_id).order_by('order_num')
    else:
        qs = Slide.objects.filter(meeting=meeting_id,group_acronym_id=group_id).order_by('order_num')
    
    # if direction is up and we aren't already the first slide
    if direction == 'up' and slide_id != str(qs[0].id):
        index = find_index(slide_id, qs)
        slide_before = qs[index-1]
        slide_before.order_num, slide.order_num = slide.order_num, slide_before.order_num
        slide.save()
        slide_before.save()

    # if direction is down, more than one slide and we aren't already the last slide
    if direction == 'down' and qs.count() > 1 and slide_id != str(qs[qs.count()-1].id):
        index = find_index(slide_id, qs)
        slide_after = qs[index+1]
        slide_after.order_num, slide.order_num = slide.order_num, slide_after.order_num
        slide.save()
        slide_after.save()

    url = reverse('proceedings_upload_unified', kwargs={'meeting_id':meeting_id,'group_id':group_id})
    return HttpResponseRedirect(url)

@check_permissions
def replace_slide(request, meeting_id, group_id, slide_id):
    '''
    This view allows the user to upload a new file to replace a slide.
    '''
    # we need to pass group to the template for the breadcrumbs
    group = get_group_or_404(group_id)
    slide = get_materials_object(meeting_id,'slide',slide_id)

    if request.method == 'POST': # If the form has been submitted...
        button_text = request.POST.get('submit', '')
        if button_text == 'Cancel':
            url = reverse('proceedings_upload_unified', kwargs={'meeting_id':slide.meeting.pk,'group_id':slide.group_acronym_id})
            return HttpResponseRedirect(url)
            
        form = ReplaceSlideForm(request.POST,request.FILES,instance=slide) # A form bound to the POST data
        if form.is_valid(): 
            # log activity
            text = "slide '%s' was re-uploaded" % (form.cleaned_data['slide_name']) 
            log_activity(group_id,text,meeting_id,request.person)
            
            new_slide = form.save(commit=False)
            
            # handle if the file extension changed
            file = request.FILES[request.FILES.keys()[0]]
            file_ext = os.path.splitext(file.name)[1]
            if file_ext in ('.ppt','.pptx'):
                new_slide.in_q = 1
            else:
                new_slide.in_q = 0
            new_slide.slide_type_id = Slide.REVERSE_SLIDE_TYPES[file_ext.lstrip('.').lower()]
            
            new_slide.save()
            
            filename = '%s-%s%s' % (group.acronym, new_slide.slide_num, file_ext)
            handle_upload_file(file,filename,new_slide.meeting,'slides')
                
            # rebuild proceedings.html
            # create_proceedings(slide.meeting.pk)
            url = reverse('proceedings_upload_unified', kwargs={'meeting_id':slide.meeting.pk,'group_id':slide.group_acronym_id})
            return HttpResponseRedirect(url)
    else:
        form = ReplaceSlideForm(instance=slide)
    
    return render_to_response('proceedings/replace_slide.html',{
        'group': group,
        'interim': is_interim_meeting(meeting_id),
        'meeting':slide.meeting,
        'slide':slide,
        'form':form},
        RequestContext(request, {}),
    )
    
@sec_only
def status(request,id):
    '''
    Edits the status associated with proceedings: Freeze/Unfreeze proceeding status.

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding

    '''

    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    return render_to_response('proceedings/status.html', {
        'meeting':meeting,
        'proceeding':proceeding},
        RequestContext(request,{}), 
    )
    
def select(request, meeting_id):
    '''
    A screen to select which group you want to upload material for.  Works for Secretariat staff
    and external (ADs, chairs, etc)
    '''
    if request.method == 'POST':
        redirect_url = reverse('proceedings_upload_unified', kwargs={'meeting_id':meeting_id,'group_id':request.POST['group']})
        return HttpResponseRedirect(redirect_url)
        
    meeting = get_object_or_404(Meeting, meeting_num=meeting_id)
    proceeding = get_object_or_404(Proceeding, meeting_num=meeting_id)

    # TODO
    # if the meeting is current use query for groups with meetings scheduled
    # if meeting is previous, get all.  see get_groups_list in old app
    '''
    max_meeting_num = Proceeding.objects.aggregate(Max('meeting_num'))['meeting_num__max']
    
    # Group Selection dropdown criteria
    # If the passed meeting number is the latest meeting number then use "meeting_scheduled" field
    # If the passed meeting number is not the latest meeting number then use "meeting_scheduled_old" field
    
    is_max = True if str(max_meeting_num) == str(id) else False
    if str(max_meeting_num) == str(id):
        is_max = True
        meeting_scheduled_field='meeting_scheduled'
    else:
        is_max = False
        meeting_scheduled_field='meeting_scheduled_old'
    
    from forms:
    SEARCH_GROUP_CHOICES_SCHEDULED = list( Acronym.objects.filter(ietfwg__meeting_scheduled__exact='YES').values_list('acronym_id','acronym').order_by('acronym'))
    SEARCH_GROUP_CHOICES_NOT_SCHEDULED = list( Acronym.objects.filter(ietfwg__meeting_scheduled_old__exact='YES').values_list('acronym_id','acronym').order_by('acronym'))
    '''
    
    if request.user_is_secretariat:
        # initialize working groups form
        choices = build_choices(IETFWG.objects.filter(status=1, meeting_scheduled="YES"))
        group_form = GroupSelectForm(choices=choices)
        
        # intialize IRTF form
        choices = build_choices(IRTF.objects.filter(meeting_scheduled=True))
        irtf_form = GroupSelectForm(choices=choices)
        
        # initialize Training form
        #choices = build_choices(Acronym.objects.filter(acronym_id__lt=-2))
        training_sessions = [ Acronym.objects.get(acronym_id=a.group_acronym_id) for a in WgMeetingSession.objects.filter(meeting=meeting.meeting_num,group_acronym_id__lt=-2)]
        choices = build_choices(training_sessions)
        training_form = GroupSelectForm(choices=choices)
    else:
        groups = get_my_groups(request)
        choices = build_choices(groups)
        group_form = GroupSelectForm(choices=choices)
        
        irtfs = [ x.irtf for x in request.person.irtfchair_set.all() if x.irtf.meeting_scheduled]
        choices = build_choices(irtfs)
        irtf_form = GroupSelectForm(choices=choices)
        
        training_form = None
    
    return render_to_response('proceedings/select.html', {
        'group_form': group_form,
        'irtf_form': irtf_form,
        'training_form': training_form,
        'meeting':meeting,
        'proceeding':proceeding},
        RequestContext(request,{}), 
    )
    
def select_interim(request):
    '''
    A screen to select which group you want to upload Interim material for.  Works for Secretariat staff
    and external (ADs, chairs, etc)
    '''
    if request.method == 'POST':
        redirect_url = reverse('proceedings_interim', kwargs={'group_id':request.POST['group']})
        return HttpResponseRedirect(redirect_url)
    
    if request.user_is_secretariat:
        # initialize working groups form
        choices = build_choices(IETFWG.objects.filter(status=1, meeting_scheduled="YES"))
        group_form = GroupSelectForm(choices=choices)
        
        # per Alexa, not supporting Interim IRTF meetings at this time
        # intialize IRTF form
        #choices = build_choices(IRTF.objects.all())
        #choices = build_choices(IRTF.objects.filter(meeting_scheduled=True))
        #irtf_form = GroupSelectForm(choices=choices)
        
    else:
        # these forms aren't used for non-secretariat
        groups = get_my_groups(request)
        choices = build_choices(groups)
        group_form = GroupSelectForm(choices=choices)
        irtf_form = None
        training_form = None
    
    return render_to_response('proceedings/interim_select.html', {
        'group_form': group_form},
        #'irtf_form': irtf_form,
        RequestContext(request,{}), 
    )
    
@sec_only
def upload_presentation(request,id,slide_id):
    '''
    Handles the upload process for the converted slide files.
      
    The files are in PPT/PPTX format. Manual downlaod and conversion to PDF is performed. 
    
    **Templates:**

    * ``proceedings/upload_presentation.html``

    **Template Variables:**

    * meeting,upload_presentation,slide

    '''
    meeting = get_object_or_404(Meeting, meeting_num=id)
    slide = get_object_or_404(Slide,id=slide_id)

    if request.method == 'POST':
        upload_presentation  = UploadPresentationForm(request.POST,request.FILES)
        if upload_presentation.is_valid():
            file = request.FILES[request.FILES.keys()[0]]
            base, extension = os.path.splitext(file.name)
            file_name = '%s-%s%s' % (slide.group_name, slide.slide_num, extension)
            handle_presentation_upload(file,file_name,meeting)
            slide.slide_type_id = Slide.REVERSE_SLIDE_TYPES[extension.lstrip('.').lower()]
            slide.slide_name = upload_presentation.cleaned_data['slide_name']
            slide.in_q = 0
            slide.save()

            messages.success(request,'Presentation file uploaded sucessfully')
            url = reverse('proceedings_convert', kwargs={'id':id})
            return HttpResponseRedirect(url)

    else:
         upload_presentation = UploadPresentationForm(initial={'slide_name': slide.slide_name})

    return render_to_response('proceedings/upload_presentation.html', {
               'meeting': meeting,
               'upload_presentation': upload_presentation,
               'slide': slide},
       RequestContext(request, {}),
    )
    
@check_permissions
def upload_unified(request, meeting_id, group_id):
    '''
    This view is the main view for uploading / re-ordering material for regular and interim
    meetings.
    '''
    
    meeting = get_meeting_or_404(meeting_id)
    group = get_group_or_404(group_id)
    activities = WgProceedingsActivity.objects.filter(meeting_num=meeting_id,group_acronym_id=group_id)
    
    # Initialize -------------------------------
    irtf = 0
    interim = 0
    slide_class = Slide

    # this identification should happen at another layer, but all this will go away 
    # with new db schema
    if 0 < int(group_id) < 100:
        irtf = 1
    if is_interim_meeting(meeting_id):
        interim = 1
        slide_class = InterimSlide
    
    if request.method == 'POST':
        button_text = request.POST.get('submit','')
        if button_text == 'Back':
            if interim:
                url = reverse('proceedings_interim', kwargs={'group_id':group.pk})
            else:
                url = reverse('proceedings_select', kwargs={'meeting_id':meeting_id})
            return HttpResponseRedirect(url)
        
        form = UnifiedUploadForm(request.POST,request.FILES)
        if form.is_valid():
            material_type = form.cleaned_data['material_type']
            slide_name =  form.cleaned_data['slide_name']
            
            file = request.FILES[request.FILES.keys()[0]]
            file_ext = os.path.splitext(file.name)[1]
            if file_ext in ('.ppt','.pptx'):
                in_q = 1
            else:
                in_q = 0
                
            #Depending upon the material  type(ie Presentation/Agenda/Minute) perform relevant actions
            #If Uploaded material is slide-presentation#
            #------------------------------------------
            if material_type == 1:
                order_num = get_next_order_num(meeting,group)
                slide_num = get_next_slide_num(meeting,group)
                
                filename = '%s-%s%s' % (group.acronym, slide_num, file_ext)
                slide_type_id = Slide.REVERSE_SLIDE_TYPES[file_ext.lstrip('.').lower()]
                subdir = 'slides'
                handle_upload_file(file,filename,meeting,subdir)
                slide_obj = slide_class(meeting=meeting,
                                  group_acronym_id=group_id,
                                  slide_num=slide_num,
                                  order_num=order_num,
                                  slide_type_id=slide_type_id,
                                  slide_name=slide_name,
                                  irtf=irtf,
                                  interim=interim,
                                  in_q=in_q)
                slide_obj.save()
                
                # log activity
                text = "slide, '%s', was uploaded" % slide_name
                log_activity(group_id,text,meeting_id,request.person)
            
            #If Uploaded material is agenda/minute#
            #------------------------------------------
            else:
                filename = group.acronym + file_ext
                if material_type == 2:
                    subdir = 'minutes'
                    if not interim:
                        dynamic_model = get_model('proceedings','Minute')
                    else:
                        dynamic_model = get_model('proceedings','InterimMinute')
                else:
                    subdir = 'agenda'
                    if not interim:
                        dynamic_model = get_model('proceedings','WgAgenda')
                    else:
                        dynamic_model = get_model('proceedings','InterimAgenda')
                
                handle_upload_file(file,filename,meeting,subdir)

                # because Minute and WgAgenda models have the same fields we can use
                # one routine to create the new record if it doesn't already exist
                obj, created = dynamic_model.objects.get_or_create(
                    meeting=meeting,
                    group_acronym_id=group_id,
                    irtf=irtf,
                    interim=interim,
                    defaults={'filename':filename})

                # log activity
                text = "%s was uploaded" % subdir
                log_activity(group_id,text,meeting_id,request.person)
                
            create_proceedings(meeting)
            messages.success(request,'File uploaded sucessfully')
    
    else:
        form = UnifiedUploadForm(initial={'meeting_id':meeting.pk, 'group_id':group.pk})
    
    slides = get_slides(meeting,group)
    minutes = get_minutes(meeting,group)
    agenda = get_agenda(meeting,group)
    
    # setup proceedings url
    if os.path.exists(meeting.get_proceedings_path(group)):
        proceedings_url = meeting.get_proceedings_url(group)
    else:
        proceedings_url = ''
    
    return render_to_response('proceedings/upload_unified.html', {
        'activities': activities,
        'interim': interim,
        'meeting': meeting,
        'group': group,
        'minutes': minutes,
        'agenda': agenda,
        'form': form,
        'slides':slides,
        'proceedings_url': proceedings_url},
        RequestContext(request, {}),
    )
    
def view(request, id):
    '''
    View Meeting information.

    **Templates:**

    * ``proceedings/view.html``

    **Template Variables:**

    * meeting , proceeding

    '''
    meeting = get_object_or_404(Meeting, meeting_num=id)
    proceeding = get_object_or_404(Proceeding, meeting_num=id)

    if not request.user_is_secretariat:
        url = reverse('proceedings_select', kwargs={'meeting_id':id})
        return HttpResponseRedirect(url)
    
    return render_to_response('proceedings/view.html', {
        'meeting': meeting,
        'proceeding': proceeding},
        RequestContext(request, {}),
    )
































