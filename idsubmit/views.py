# Copyright The IETF Trust 2007, All Rights Reserved

# Create your views here.
#import models
from models import IdSubmissionDetail
from ietf.idtracker.models import Acronym, IETFWG, InternetDraft
from django.shortcuts import render_to_response as render, get_object_or_404
#from ietf.proceedings.models import Meeting, Switches
#from django.views.generic.list_detail import object_list
#from django.http import HttpResponsePermanentRedirect, Http404
#from django.db.models import Q
from ietf.idsubmit.forms import IDUploadForm
import re
# function parse_meta_data
# This function extract filename, revision, abstract, title, and
# author's information from the passed I-D content
def parse_meta_data (id_content):
    not_found = "Not Found"
    filesize = len(id_content)
    #extract filename and revision
    filename_re = re.search('\n {3,}<{0,1}((draft-.+)-(\d\d)).+\n',id_content)
    try: 
        filename = filename_re.group(2)
        ## Need to check for invalid characters in filename here ##
    except AttributeError: filename = not_found
    try: revision = filename_re.group(3)
    except AttributeError: revision= not_found
    #extract page number
    id_content_re = re.compile('\[Page \d+\]')
    pages = id_content_re.split(id_content)
    page_num = len(pages) - 1
    #get first two pages
    first_two_pages = pages[0] + pages[1]
    #extract title
    headers_re = re.compile('\n {3,}<{0,1}((draft-.+)-(\d\d)).+\n')
    id_content = headers_re.sub('',id_content)
    title_re = re.search('\n{2,}(( +\w+.+\n)+)\n*Status of ',id_content)
    try: 
        title = title_re.group(1)
        title_re = re.compile('\s{2,}')
        title = title_re.sub('',title)
        title_re = re.compile('^\s+')
        title = title_re.sub('',title)
    except AttributeError: title = not_found 
    #remove page separator
    headers_re = re.compile('\n.+expires.+[a-zA-Z]+.+[1920]+\d\d\s*[\[]page.+[\]]\n.+\nInternet[-| ]Draft.+[a-zA-Z]+ \d\d\d\d\n',re.I)
    id_content = headers_re.sub('',id_content)
    #extract abstract
    abstract_m = re.search('\nAbstract\s*\n+(( {3,}.+\n+)+)',id_content)
    try:
        abstract = abstract_m.group(1)
        abstract_re = re.compile(' {3,}')
        abstract = abstract_re.sub('',abstract) 
        abstract_re = re.compile('\n{2,}(?![A-Z])')
        abstract = abstract_re.sub('\n',abstract) 
        ## abstract need to be validated: how about at least 120 characters ## 
    except AttributeError: abstract = not_found 
    #extract creation date
    headers_re = re.compile('expires:\s*\d*\s*[A-Za-z]+\s*\d*[,]?\s*[1920]+\d\d/',re.I)
    id_content = headers_re.sub('',id_content)
    header_re=re.compile('expiration date:\s*\d*\s*[A-Za-z]+\s*\d*[,]?\s*[1920]+\d\d/')
    id_content = headers_re.sub('',id_content)
    creation_date_re = re.search('\s*(\d*\s{0,1}[A-Za-z]+\s*\d*[,]?\s+[1920]+\d\d)',id_content)
    try: creation_date = creation_date_re.group(1)
    except AttributeError: creation_date = not_found 
    ## creation_date needs to be formated here? ##
    #extract authors' name and email
    #authors_info = []
    authors_section = re.search('\nAuthor.+\n+(( {3,}.+\n+)+)',id_content)
    try: authors_info = authors_section.group(1)
    except AttributeError: authors_info = not_found
    wg =  group = Acronym.objects.get(acronym='none')
    meta_data_fields = {
        'filename': filename,
        'revision': revision,
        'title': title,
        'group': wg,
        'creation_date':"2007-1-1",
        'file_type': "txt",
        'abstract': abstract,
        'filesize': filesize,
        'first_two_pages': first_two_pages,
        'txt_page_count': page_num,
    }
    return {'result':1,'authors_info':authors_info, 'meta_data_fields':meta_data_fields}

def file_upload(request):
    #form = NONE
    if request.POST:
        post_data = request.POST.copy()
        post_data.update(request.FILES)
        form = IDUploadForm(post_data)
        if form.is_valid():
            file_content = form.file_content()
            content = file_content['content']
            content_type = file_content['content-type']
            if content_type != 'text/plain':
                return render("idsubmit/error.html",\
                               {'error_msg':"Not plain text"})
            data = parse_meta_data(content)
            meta_data = data['meta_data_fields']
            if data['result']:
                content = form.save(meta_data['filename'],meta_data['revision'])
                list = IdSubmissionDetail(**meta_data)
                try: list.save()
                except AttributeError:
                    return  render("idsubmit/error.html",\
                               {'error_msg':"Data Saving Error"})
                pass
            return render("idsubmit/validate.html",{'meta_data':meta_data})
        else:
            form = IDUploadForm()
    else:
        form = IDUploadForm()
    return render ("idsubmit/upload.html",{'form':form})

