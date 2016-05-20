from django.conf.urls import patterns, url
from ietf.doc import views_review

urlpatterns = patterns('',
    url(r'^$', views_review.request_review),
    url(r'^(?P<request_id>[0-9]+)/$', views_review.review_request),
    url(r'^(?P<request_id>[0-9]+)/withdraw/$', views_review.withdraw_request),
)

