# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns
from ietf.idtracker.models import Area, IETFWG

urlpatterns = patterns('django.views.generic.list_detail',
     (r'^area/$', 'object_list', { 'queryset': Area.objects.filter(status=1).select_related().order_by('acronym.acronym'), 'template_name': 'mailinglists/areas_list.html' }),
     (r'^wg/$', 'object_list', { 'queryset': IETFWG.objects.filter(email_archive__startswith='http'), 'template_name': 'mailinglists/wgwebmail_list.html' }),
)
urlpatterns += patterns('',
     (r'^nonwg/$', 'django.views.generic.simple.redirect_to', { 'url': 'http://www.ietf.org/list/nonwg.html'}),
     (r'^nonwg/update/$', 'django.views.generic.simple.redirect_to', { 'url': 'http://www.ietf.org/list/nonwg.html'}),
     (r'^request/$', 'django.views.generic.simple.redirect_to', { 'url': 'http://www.ietf.org/list/request.html' }),
)
