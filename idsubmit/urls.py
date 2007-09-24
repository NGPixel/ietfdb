# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idsubmit import views
#from ietf.idsubmit.models import TelechatMinutes
#from ietf.idsubmit.models import BallotInfo

urlpatterns = patterns('django.views.generic.simple',
     (r'^$', 'direct_to_template', {'template': 'idsubmit/upload.html'}),
     (r'^status/$', 'direct_to_template', {'template': 'idsubmit/status.html'}),
     (r'^adjust/$', 'direct_to_template', {'template': 'idsubmit/adjust.html'}),
)

urlpatterns += patterns('',
     (r'^upload/$', views.file_upload),
)

