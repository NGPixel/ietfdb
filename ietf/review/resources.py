# Autogenerated by the makeresources management command 2016-06-14 04:21 PDT
from tastypie.resources import ModelResource
from tastypie.fields import ToManyField                 # pyflakes:ignore
from tastypie.constants import ALL, ALL_WITH_RELATIONS  # pyflakes:ignore
from tastypie.cache import SimpleCache

from ietf import api
from ietf.api import ToOneField                         # pyflakes:ignore

from ietf.review.models import (ReviewerSettings, ReviewRequest,
                                ResultUsedInReviewTeam, TypeUsedInReviewTeam,
                                UnavailablePeriod, ReviewWish, NextReviewerInTeam,
                                ReviewSecretarySettings)


from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class ReviewerSettingsResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = ReviewerSettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewer'
        filtering = { 
            "id": ALL,
            "min_interval": ALL,
            "filter_re": ALL,
            "skip_next": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewerSettingsResource())

from ietf.doc.resources import DocumentResource
from ietf.group.resources import RoleResource, GroupResource
from ietf.name.resources import ReviewRequestStateNameResource, ReviewResultNameResource, ReviewTypeNameResource
class ReviewRequestResource(ModelResource):
    state            = ToOneField(ReviewRequestStateNameResource, 'state')
    type             = ToOneField(ReviewTypeNameResource, 'type')
    doc              = ToOneField(DocumentResource, 'doc')
    team             = ToOneField(GroupResource, 'team')
    reviewer         = ToOneField(RoleResource, 'reviewer', null=True)
    review           = ToOneField(DocumentResource, 'review', null=True)
    result           = ToOneField(ReviewResultNameResource, 'result', null=True)
    class Meta:
        queryset = ReviewRequest.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewrequest'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "deadline": ALL,
            "requested_rev": ALL,
            "reviewed_rev": ALL,
            "state": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
            "team": ALL_WITH_RELATIONS,
            "reviewer": ALL_WITH_RELATIONS,
            "review": ALL_WITH_RELATIONS,
            "result": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewRequestResource())



from ietf.group.resources import GroupResource
from ietf.name.resources import ReviewResultNameResource
class ResultUsedInReviewTeamResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    result           = ToOneField(ReviewResultNameResource, 'result')
    class Meta:
        queryset = ResultUsedInReviewTeam.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'resultusedinreviewteam'
        filtering = { 
            "id": ALL,
            "team": ALL_WITH_RELATIONS,
            "result": ALL_WITH_RELATIONS,
        }
api.review.register(ResultUsedInReviewTeamResource())



from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class UnavailablePeriodResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = UnavailablePeriod.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'unavailableperiod'
        filtering = { 
            "id": ALL,
            "start_date": ALL,
            "end_date": ALL,
            "availability": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(UnavailablePeriodResource())

from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
from ietf.doc.resources import DocumentResource
class ReviewWishResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    doc              = ToOneField(DocumentResource, 'doc')
    class Meta:
        queryset = ReviewWish.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewwish'
        filtering = { 
            "id": ALL,
            "time": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
            "doc": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewWishResource())



from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class NextReviewerInTeamResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    next_reviewer    = ToOneField(PersonResource, 'next_reviewer')
    class Meta:
        queryset = NextReviewerInTeam.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'nextreviewerinteam'
        filtering = { 
            "id": ALL,
            "team": ALL_WITH_RELATIONS,
            "next_reviewer": ALL_WITH_RELATIONS,
        }
api.review.register(NextReviewerInTeamResource())



from ietf.group.resources import GroupResource
from ietf.name.resources import ReviewTypeNameResource
class TypeUsedInReviewTeamResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    type             = ToOneField(ReviewTypeNameResource, 'type')
    class Meta:
        queryset = TypeUsedInReviewTeam.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'typeusedinreviewteam'
        filtering = { 
            "id": ALL,
            "team": ALL_WITH_RELATIONS,
            "type": ALL_WITH_RELATIONS,
        }
api.review.register(TypeUsedInReviewTeamResource())



from ietf.person.resources import PersonResource
from ietf.group.resources import GroupResource
class ReviewSecretarySettingsResource(ModelResource):
    team             = ToOneField(GroupResource, 'team')
    person           = ToOneField(PersonResource, 'person')
    class Meta:
        queryset = ReviewSecretarySettings.objects.all()
        serializer = api.Serializer()
        cache = SimpleCache()
        #resource_name = 'reviewsecretarysettings'
        filtering = { 
            "id": ALL,
            "remind_days_before_deadline": ALL,
            "team": ALL_WITH_RELATIONS,
            "person": ALL_WITH_RELATIONS,
        }
api.review.register(ReviewSecretarySettingsResource())

