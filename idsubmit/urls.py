# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idsubmit import views
#from ietf.idsubmit.models import TelechatMinutes
from ietf.idsubmit.models import IdSubmissionDetail 

queryset_idsubmit = IdSubmissionDetail.objects.all()
urlpatterns = patterns('django.views.generic.simple',
     (r'^status/$', 'direct_to_template', {'template': 'idsubmit/status.html'}),
     (r'^adjust/$', 'direct_to_template', {'template': 'idsubmit/adjust.html'}),
)

urlpatterns += patterns('',
     (r'^$', views.file_upload),
     (r'^upload/$', views.file_upload),
)
urlpatterns += patterns('django.views.generic.list_detail',
        (r'^viewfirsttwo/(?P<object_id>\d+)/$', 'object_detail', { 'queryset': queryset_idsubmit, 'template_name':"idsubmit/first_two_pages.html" }),
)
