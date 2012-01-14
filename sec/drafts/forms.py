from django import forms
from django.forms.formsets import BaseFormSet

from redesign.doc.models import *
from redesign.name.models import IntendedStdLevelName
from redesign.group.models import Group

from sec.utils.ams_utils import get_base, get_revision

import datetime
import re
from os.path import splitext

# ---------------------------------------------
# Select Choices 
# ---------------------------------------------
WITHDRAW_CHOICES = (('ietf','Withdraw by IETF'),('author','Withdraw by Author'))

# ---------------------------------------------
# Custom Fields 
# ---------------------------------------------
class DocumentField(forms.FileField):
    '''A validating document upload field'''
    valid_file_extensions = ('txt','pdf','ps','xml')
    unique = False
    
    def __init__(self, valid_file_extensions=None, unique=False, *args, **kwargs):
        super(DocumentField, self).__init__(*args, **kwargs)
        if unique:
            self.unique = unique
        if valid_file_extensions:
            self.valid_file_extensions = valid_file_extensions

    def clean(self, data, initial=None):
        file = super(DocumentField, self).clean(data,initial)
        # this is redundant to regex below
        #ext = splitext(file.name)[1][1:].lower()
        #if ext not in self.valid_file_extensions:
        #    raise forms.ValidationError('Document types accepted: ' + ', '.join(self.valid_file_extensions))
        if file:
            # ensure file name complies with standard format
            m = re.search(r'.*-\d{2}\.(txt|pdf|ps|xml)', file.name)
            if file and not m:
                raise forms.ValidationError('File name must be in the form base-NN.[txt|pdf|ps|xml]')
            # ensure that base name is not already used
            if self.unique:
                if Document.objects.filter(name=get_base(file.name)).count() > 0:
                    raise forms.ValidationError('This document already exists! (%s)' % get_base(file.name)) 

        return file

class MyModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.acronym

# ---------------------------------------------
# Forms 
# ---------------------------------------------
class AddFileForm(forms.Form):
    # it appears the file input widget is not stylable via css
    file = DocumentField(unique=True)
    
class AddModelForm(forms.ModelForm):
    #file = DocumentField(unique=True)
    #file2 = DocumentField(required=False)
    start_date = forms.DateField()
    group = MyModelChoiceField(queryset=Group.objects.active_wgs().order_by('acronym'), required=True)
    
    class Meta:
        model = Document
        # remove replaced_by,review_by_rfc_editor fields from list per secretariat staff 09-27-10
        # remove local_path per Glen, staff 12-02-10
        fields = ('title','group','stream','start_date','pages','abstract','internal_comments')
       
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(AddModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].label='Document Name'
        self.fields['title'].widget=forms.Textarea()
        #self.fields['group'].queryset=Group.objects.active_wgs().order_by('acronym')
        #self.fields['group'].widget = MyModelChoiceField(queryset=Group.objects.active_wgs().order_by('acronym'))
        self.fields['start_date'].initial=datetime.date.today
        self.fields['pages'].label='Number of Pages'
        self.fields['internal_comments'].label='Comments'

    # Validation: all upload files must have the same base name
    '''
    def clean(self):
        super(AddModelForm, self).clean()
        cleaned_data = self.cleaned_data
        file = cleaned_data.get('file')
        file2 = cleaned_data.get('file2')
        if file and file2:
            if get_base(file.name) != get_base(file2.name):
                raise forms.ValidationError('Uploaded files must have the same base name.')

        # Always return the full collection of cleaned data.
        return cleaned_data

    
    def save(self, force_insert=False, force_update=False, commit=True):
        self.intended_status = IDIntendedStatus.objects.get(intended_status_id=8)
        assert False, self
        m = super(AddModelForm, self).save(commit=False)
        # do custom stuff
        if commit:
            m.save()
        return m
    '''

class AuthorForm(forms.Form):
    #author_name = forms.CharField(max_length=100,label='Name',help_text="To see a list of people type the first name, or last name, or both.")
    author_name = forms.CharField(max_length=100,label='Name')

    # set css class=name-autocomplete for name field (to provide select list)
    def __init__(self, *args, **kwargs):
        super(AuthorForm, self).__init__(*args, **kwargs)
        self.fields['author_name'].widget.attrs['class'] = 'name-autocomplete'

    # check for tag within parenthesis to ensure name was selected from the list 
    def clean_author_name(self):
        name = self.cleaned_data.get('author_name', '')
        m = re.search(r'(\d+)', name)
        if name and not m:
            raise forms.ValidationError("You must select an entry from the list!") 
        return name

class BaseFileFormSet(BaseFormSet):
    '''
    This class is used when creating the formset factory for file upload,
    so we can call perform vailations across multiple file upload forms
    '''
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(BaseFileFormSet, self).__init__(*args, **kwargs)
        
    def clean(self):
        # Checks that all files have the same base
        if any(self.errors):
            # Don't bother validating the formset unless each form is valid on its own
            return
        #assert False, self.total_form_count()
        names = []
        for i in range(0, self.total_form_count()):
            form = self.forms[i]
            if form.has_changed():
                file = form.cleaned_data['file']
                base = splitext(file.name)[0]
                if base not in names:
                    names.append(base)
        if len(names) > 1:
            raise forms.ValidationError, "All files must have the same base name"
        
        # if 'draft' exists in the session dictionary we are uploading files to an existing
        # draft (as opposed to adding a new draft) so do extra validations
        if 'draft' in self.request.session:
            draft = self.request.session['draft']
            # Check that the upload base filename is the same as the draft base filename
            upload_base = get_base(names[0])
            draft_base = draft.name
            if upload_base != draft_base:
                raise forms.ValidationError, "The upload filename (%s) is different than the draft filename (%s)" % (upload_base, draft_base)
                
            # Check that the revision number of the upload file is current revision + 1
            next_revision = str(int(draft.rev)+1).zfill(2)
            if names[0][-2:] != next_revision:
                raise forms.ValidationError, "Expected revision # %s" % (next_revision)

class EditModelForm(forms.ModelForm):
    #expiration_date = forms.DateField(required=False)
    #state = forms.ModelChoiceField(queryset=State.objects.filter(type='draft'),empty_label=None)
    group = MyModelChoiceField(queryset=Group.objects.active_wgs().order_by('acronym'), required=True)
    review_by_rfc_editor = forms.BooleanField(required=False)
    
    class Meta:
        model = Document
        fields = ('title','group','review_by_rfc_editor','name','rev','pages','abstract','internal_comments')
                 
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(EditModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].label='Document Name'
        self.fields['title'].widget=forms.Textarea()
        self.fields['rev'].widget.attrs['size'] = 2
        self.fields['abstract'].widget.attrs['cols'] = 72
        # setup special fields
        if self.instance:
            # setup replaced
            self.fields['review_by_rfc_editor'].initial = bool(self.instance.tags.filter(slug='rfc-rev'))
            
    def save(self, force_insert=False, force_update=False, commit=True):
        m = super(EditModelForm, self).save(commit=False)
        
        if 'state' in self.changed_data:
            m.set_state(self.cleaned_data['state'])
        
        if 'review_by_rfc_editor' in self.changed_data:
            if self.cleaned_data.get('review_by_rfc_editor',''):
                m.tags.add('rfc-rev')
            else:
                m.tags.remove('rfc-rev')
        
        # handle replaced by
        
        if commit:
            m.save()
        return m

    # field must contain filename of existing draft
    def clean_replaced_by(self):
        name = self.cleaned_data.get('replaced_by', '')
        if name and not InternetDraft.objects.filter(filename=name):
            raise forms.ValidationError("ERROR: Draft does not exist") 
        return name
        
    def clean(self):
        super(EditModelForm, self).clean()
        cleaned_data = self.cleaned_data
        """
        expiration_date = cleaned_data.get('expiration_date','')
        status = cleaned_data.get('status','')
        replaced = cleaned_data.get('replaced',False)
        replaced_by = cleaned_data.get('replaced_by','')
        replaced_status_object = IDStatus.objects.get(status_id=5)
        expired_status_object = IDStatus.objects.get(status_id=2)
        # this condition seems to be valid
        #if expiration_date and status != expired_status_object:
        #    raise forms.ValidationError('Expiration Date set but status is %s' % (status))
        if status == expired_status_object and not expiration_date:
            raise forms.ValidationError('Status is Expired but Expirated Date is not set')
        if replaced and status != replaced_status_object:
            raise forms.ValidationError('You have checked Replaced but status is %s' % (status))
        if replaced and not replaced_by:
            raise forms.ValidationError('You have checked Replaced but Replaced By field is empty')
        """
        return cleaned_data

class EmailForm(forms.Form):
    # max_lengths come from db limits, cc is not limited
    to = forms.CharField(max_length=255)
    cc = forms.CharField(required=False)
    subject = forms.CharField(max_length=255)
    body = forms.CharField(widget=forms.Textarea())

class ExtendForm(forms.Form):
    revision_date = forms.DateField()
    
class ReplaceForm(forms.Form):
    replaced_by = forms.CharField(max_length=100,help_text='Enter the filename of the Draft which replaces this one.')

    def __init__(self, draft, *args, **kwargs):
        self.draft = draft
        super(ReplaceForm, self).__init__(*args, **kwargs)
        
    # field must contain filename of existing draft
    def clean_replaced_by(self):
        name = self.cleaned_data.get('replaced_by', '')
        if name and not InternetDraft.objects.filter(filename=name):
            raise forms.ValidationError("ERROR: Draft does not exist")
        if name == self.draft.filename:
            raise forms.ValidationError("ERROR: A draft can't replace itself")
        return name

class BaseRevisionModelForm(forms.ModelForm):
    revision_date = forms.DateField()
    
    class Meta:
        model = Document
        fields = ('title','revision_date','pages','abstract')

class RevisionFileForm(forms.Form):
    # it appears the file input widget is not stylable via css
    file = DocumentField()
    # we need this hidden field for validation
    # draft = forms.CharField(widget=forms.HiddenInput())

class RevisionModelForm(forms.ModelForm):
    # file = DocumentField()
    revision_date = forms.DateField()
    
    class Meta:
        model = Document
        fields = ('title','revision_date','pages','abstract')
    
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(RevisionModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].label='Document Name'
        self.fields['title'].widget=forms.Textarea()
        self.fields['pages'].label='Number of Pages'
        
    # ensure basename is same as existing 
    '''
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if get_base(file.name) != self.instance.filename:
            raise forms.ValidationError("Basename doesn't match (%s)" % self.instance.filename)
        if int(get_revision(file.name)) != int(self.instance.revision) + 1:
            raise forms.ValidationError("File doesn't match next revision # (%s)" % str(int(self.instance.revision)+1).zfill(2))
        return file
    '''

class RevisionForm(forms.Form):
    abstract = forms.CharField(widget=forms.Textarea())
    txt_page_count = forms.IntegerField(label='Number of Pages')
    file = DocumentField()
    draft = forms.CharField(widget=forms.HiddenInput())
    
    # ensure basename is same as existing 
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if get_base(file.name) != self.instance.filename:
            raise forms.ValidationError("Basename doesn't match (%s)" % self.instance.filename)
        return file
        
class RfcModelForm(forms.ModelForm):
    rfc_number = forms.IntegerField()
    rfc_published_date = forms.DateField(initial=datetime.datetime.now)
    #proposed_date = forms.DateField(required=False)
    #draft_date = forms.DateField(required=False)
    #standard_date = forms.DateField(required=False)
    #historic_date = forms.DateField(required=False)
    fyi_number = forms.IntegerField(required=False)
    std_number = forms.IntegerField(required=False)
    group = MyModelChoiceField(queryset=Group.objects.active_wgs().order_by('acronym'), required=True)
    
    class Meta:
        model = Document
        fields = ('title','group','pages','std_level','internal_comments')
    
    # use this method to set attrs which keeps other meta info from model.  
    def __init__(self, *args, **kwargs):
        super(RfcModelForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget = forms.Textarea()
        self.fields['std_level'].required = True
    
    def save(self, force_insert=False, force_update=False, commit=True):
        obj = super(RfcModelForm, self).save(commit=False)
        
        # create DocAlias
        DocAlias.objects.create(document=self.instance,name="rfc%d" % self.cleaned_data['rfc_number'])
        
        if commit:
            obj.save()
        return obj
        
    def clean_rfc_number(self):
        rfc_number = self.cleaned_data['rfc_number']
        if DocAlias.objects.filter(name='rfc' + str(rfc_number)):
            raise forms.ValidationError("RFC %d already exists" % rfc_number)
        return rfc_number
        
class RfcObsoletesForm(forms.Form):
    relation = forms.ModelChoiceField(queryset=DocRelationshipName.objects.filter(slug__in=('updates','obs')),required=False)
    rfc = forms.IntegerField(required=False)
    
    # ensure that RFC exists
    def clean_rfc(self):
        rfc = self.cleaned_data.get('rfc','')
        if rfc:
            try:
                test = Rfc.objects.get(rfc_number=rfc)
            except Rfc.DoesNotExist:
                raise forms.ValidationError("RFC does not exist")
        return rfc
    
    def clean(self):
        super(RfcObsoletesForm, self).clean()
        cleaned_data = self.cleaned_data
        relation = cleaned_data.get('relation','')
        rfc = cleaned_data.get('rfc','')
        if (relation and not rfc) or (rfc and not relation):
            raise forms.ValidationError('You must select a relation and enter RFC #')
        return cleaned_data

class SearchForm(forms.Form):
    intended_std_level = forms.ModelChoiceField(queryset=IntendedStdLevelName.objects,label="Intended Std Level",required=False)
    document_title = forms.CharField(max_length=80,label='Document Title',required=False)
    group = forms.CharField(max_length=12,required=False)
    name = forms.CharField(max_length=80,required=False)
    state = forms.ModelChoiceField(queryset=State.objects.filter(type='draft'),required=False)
    revision_date_start = forms.DateField(label='Revision Date (start)',required=False)
    revision_date_end = forms.DateField(label='Revision Date (end)',required=False)

class WithdrawForm(forms.Form):
    type = forms.CharField(widget=forms.Select(choices=WITHDRAW_CHOICES),help_text='Select which type of withdraw to perform')

