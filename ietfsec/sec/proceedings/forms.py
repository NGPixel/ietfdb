from django import forms
from django.conf import settings
from django.db.models import Max
from django.template.defaultfilters import filesizeformat

from sec.proceedings.models import *
from sec.core.models import *
from sec.groups.models import *

import os
import re
# ---------------------------------------------
# Globals
# ---------------------------------------------
MATERIAL_TYPE_CHOICES = (
    (1,'Presentation'),
    (2,'Minutes'),
    (3,'Agenda')
)

VALID_SLIDE_EXTENSIONS = ['.doc','.docx','.pdf','.ppt','.txt']

#----------------------------------------------------------
# Forms
#----------------------------------------------------------
class EditSlideForm(forms.ModelForm):
    class Meta:
        model = Slide
        fields = ('slide_name',)

class InterimMeetingForm(forms.Form):
    date = forms.DateField(help_text="(YYYY-MM-DD Format, please)")
    group_acronym_id = forms.CharField(widget=forms.HiddenInput())
    
    def clean(self):
        super(InterimMeetingForm, self).clean()
        cleaned_data = self.cleaned_data
        # need to use get() here, if the date field isn't valid it won't exist
        date = cleaned_data.get('date','')
        group_acronym_id = cleaned_data["group_acronym_id"]
        qs = InterimMeeting.objects.filter(start_date=date,group_acronym_id=group_acronym_id)
        if qs:
            raise forms.ValidationError('A meeting already exists for this date.')
        return cleaned_data

class ReplaceSlideForm(forms.ModelForm):
    file = forms.FileField(label='Select File')
    
    class Meta:
        model = Slide
        fields = ('slide_name',)
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        ext = os.path.splitext(file.name)[1].lower()
        if ext not in VALID_SLIDE_EXTENSIONS:
            raise forms.ValidationError('Only these file types supported for presentation slides: %s' % ','.join(VALID_SLIDE_EXTENSIONS))
        if file._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file._size)))
        return file
    
class UnifiedUploadForm(forms.Form):
    group_id = forms.CharField(widget=forms.HiddenInput())
    meeting_id = forms.CharField(widget=forms.HiddenInput())
    material_type = forms.IntegerField(widget=forms.Select(choices=MATERIAL_TYPE_CHOICES),required=True)
    slide_name = forms.CharField(label='Name of Presentation',max_length=255,required=False,help_text="For presentations only")
    file = forms.FileField(label='Select File',help_text='<div id="id_file_help">Note 1: You can only upload a presentation file in txt, pdf, doc, or ppt/pptx. System will not accept presentation files in any other format.<br><br>Note 2: All uploaded files will be available to the public immediately on the Preliminary Page. However, for the Proceedings, ppt/pptx files will be converted to html format and doc files will be converted to pdf format manually by the Secretariat staff.</div>')
    
    def clean_file(self):
        file = self.cleaned_data['file']
        if file._size > settings.MAX_UPLOAD_SIZE:
            raise forms.ValidationError('Please keep filesize under %s. Current filesize %s' % (filesizeformat(settings.MAX_UPLOAD_SIZE), filesizeformat(file._size)))
        return file
        
    def clean(self):
        super(UnifiedUploadForm, self).clean()
        # if an invalid file type is supplied no file attribute will exist
        if self.errors:
            return self.cleaned_data
        cleaned_data = self.cleaned_data
        material_type = cleaned_data['material_type']
        slide_name = cleaned_data['slide_name']
        file = cleaned_data['file']
        ext = os.path.splitext(file.name)[1].lower()

        if material_type == 1 and not slide_name:
            raise forms.ValidationError('ERROR: Name of Presentaion cannot be blank')
        
        # only supporting PDFs per Alexa 04-05-2011
        #if material_type == 1 and not file_ext[1] == '.pdf': 
        #        raise forms.ValidationError('Presentations must be a PDF file')
       
        # validate file extensions based on material type (presentation,agenda,minutes)
        # valid extensions per online documentation: meeting-materials.html
        valid_other_extensions = ['.txt','.htm','.html']
        if material_type == 1 and ext not in VALID_SLIDE_EXTENSIONS:
            raise forms.ValidationError('Only these file types supported for presentation slides: %s' % ','.join(VALID_SLIDE_EXTENSIONS))
        if material_type in (2,3) and ext not in valid_other_extensions:
            raise forms.ValidationError('Only these file types supported for minutes and agendas: %s' % ','.join(valid_other_extensions))
        
        return cleaned_data

class UploadPresentationForm(forms.Form):
    slide_name = forms.CharField(label='Name of Presentation',max_length=255,required=False)
    file = forms.FileField(label='Select File')

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if os.path.splitext(file.name)[1].lower() != '.pdf':
            raise forms.ValidationError("Only PDF files are supported")

        return file
        

        
        