from django.conf.urls import url
from ietf.sidemeeting import views

urlpatterns = [
    url(r'add/$', views.SideMeetingAddView.as_view(), name='side-meeting-add'),
    url(r'edit/(?P<pk>\d+)$', views.SideMeetingEditView.as_view(), name='side-meeting-edit'),
    url(r'delete/(?P<pk>\d+)$', views.SideMeetingDeleteView.as_view(), name='side-meeting-delete'),
    url(r'list/$', views.SideMeetingListView.as_view(), name='side-meeting-list'),
    url(r'detail/(?P<pk>\d+)/$', views.SideMeetingDetailView.as_view(), name='side-meeting-detail'),        
    url(r'thanks/$', views.SideMeetingThanksView.as_view(), name='side-meeting-thanks')    
]
