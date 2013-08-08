# Copyright The IETF Trust 2007, All Rights Reserved

from django.conf.urls.defaults import patterns, url, include
from django.views.generic.simple import redirect_to
from ietf.meeting import views
from ietf.meeting import ajax

urlpatterns = patterns('',
    (r'^(?P<meeting_num>\d+)/materials.html$', views.materials),
    (r'^agenda/$', views.html_agenda),
    (r'^agenda(?:.html)?$', views.html_agenda),
    (r'^agenda-utc(?:.html)?$', views.html_agenda_utc),
    (r'^agenda(?:.html)?$', views.agenda_html_request),
    (r'^agenda/edit$', views.edit_agenda),
    (r'^requests.html$', redirect_to, {"url": '/meeting/requests', "permanent": True}),
    (r'^requests$', views.meeting_requests),
    (r'^agenda.txt$', views.text_agenda),
    (r'^agenda/agenda.ics$', views.ical_agenda),
    (r'^agenda.ics$', views.ical_agenda),
    (r'^agenda.csv$', views.csv_agenda),
    (r'^agenda/week-view.html$', views.week_view),
    (r'^week-view.html$', views.week_view),
    (r'^(?P<num>\d+)/schedule/edit$',        views.edit_agenda),
    (r'^(?P<num>\d+)/schedule/(?P<schedule_name>[A-Za-z0-9-:_]+)/edit$',      views.edit_agenda),
    (r'^(?P<num>\d+)/schedule/(?P<schedule_name>[A-Za-z0-9-:_]+)(?:.html)?/?$', views.agenda_html_request),
    (r'^(?P<num>\d+)/agenda(?:.html)?/?$',     views.agenda_html_request),
    (r'^(?P<num>\d+)/agenda-itc(?:.html)?/?$', views.agenda_html_request),
    (r'^(?P<num>\d+)/requests.html$', redirect_to, {"url": '/meeting/%(num)s/requests', "permanent": True}),
    (r'^(?P<num>\d+)/requests$', views.meeting_requests),
    (r'^(?P<num>\d+)/agenda.txt$', views.text_agenda),
    (r'^(?P<num>\d+)/agenda.ics$', views.ical_agenda),
    (r'^(?P<num>\d+)/agenda.csv$', views.csv_agenda),
    (r'^(?P<num>\d+)/week-view.html$', views.week_view),
    (r'^(?P<num>\d+)/agenda/week-view.html$', views.week_view),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.pdf$', views.session_draft_pdf),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)-drafts.tgz$', views.session_draft_tarfile),
    (r'^(?P<num>\d+)/agenda/(?P<session>[A-Za-z0-9-]+)/?$', views.session_agenda),
    (r'^(?P<num>\d+)/session/(?P<sessionid>\d+).json',             ajax.session_json),
    (r'^(?P<num>\d+)/session/(?P<sessionid>\d+)/constraints.json', ajax.session_constraints),
    (r'^(?P<meeting_num>\d+).json$', ajax.meeting_json),
    (r'^$', views.current_materials),
)


