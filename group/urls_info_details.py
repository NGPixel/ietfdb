from django.conf.urls import patterns, url
from django.views.generic import RedirectView
import views

urlpatterns = patterns('',
    (r'^$', 'ietf.group.views.group_home', None, "group_home"),
    (r'^documents/txt/$', 'ietf.group.views.group_documents_txt'),
    (r'^documents/$', 'ietf.group.views.group_documents', None, "group_docs"),
    (r'^documents/manage/$', 'ietf.community.views.manage_list'),
    (r'^documents/csv/$', 'ietf.community.views.export_to_csv'),
    (r'^documents/feed/$', 'ietf.community.views.feed'),
    (r'^documents/subscription/$', 'ietf.community.views.subscription'),
    (r'^charter/$', 'ietf.group.views.group_about', None, 'group_charter'),
    (r'^about/$', 'ietf.group.views.group_about', None, 'group_about'),
    (r'^about/status/$', 'ietf.group.views.group_about_status'),
    (r'^about/status/edit/$', 'ietf.group.views.group_about_status_edit'),
    (r'^history/$','ietf.group.views.history'),
    (r'^email/$', 'ietf.group.views.email'),
    (r'^deps/(?P<output_type>[\w-]+)/$', 'ietf.group.views.dependencies'),
    (r'^meetings/$', 'ietf.group.views.meetings'),
    (r'^init-charter/', 'ietf.group.views_edit.submit_initial_charter'),
    (r'^edit/$', 'ietf.group.views_edit.edit', {'action': "edit"}, "group_edit"),
    (r'^conclude/$', 'ietf.group.views_edit.conclude'),
    (r'^milestones/$', 'ietf.group.milestones.edit_milestones', {'milestone_set': "current"}, "group_edit_milestones"),
    (r'^milestones/charter/$', 'ietf.group.milestones.edit_milestones', {'milestone_set': "charter"}, "group_edit_charter_milestones"),
    (r'^milestones/charter/reset/$', 'ietf.group.milestones.reset_charter_milestones', None, "group_reset_charter_milestones"),
    (r'^workflow/$', 'ietf.group.views_edit.customize_workflow'),
    (r'^materials/$', 'ietf.group.views.materials', None, "group_materials"),
    (r'^materials/new/$', 'ietf.doc.views_material.choose_material_type'),
    (r'^materials/new/(?P<doc_type>[\w-]+)/$', 'ietf.doc.views_material.edit_material', { 'action': "new" }, "group_new_material"),
    (r'^archives/$', 'ietf.group.views.derived_archives'),
    (r'^photos/$', views.group_photos),
    url(r'^email-aliases/$', RedirectView.as_view(pattern_name='ietf.group.views.email',permanent=False),name='old_group_email_aliases'),
)
