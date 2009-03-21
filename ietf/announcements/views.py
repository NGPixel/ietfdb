# Copyright The IETF Trust 2007, All Rights Reserved

# Create your views here.

from django.http import HttpResponse
from django.template.loader import render_to_string
from django.shortcuts import render_to_response

from ietf.idtracker.models import ChairsHistory
from ietf.idtracker.models import PersonOrOrgInfo
from ietf.announcements.models import Announcement

def all(request):
    curr_chair       = (ChairsHistory.objects.
                        get(chair_type='3', present_chair='1'))

    curr_chair_email = curr_chair.person.email()[1]
    curr_chair_name = curr_chair.person.email()[0]
    old_chairs         = ChairsHistory.objects.all().filter(chair_type='3',start_year__gt = 2003).order_by('-start_year')

    nomcom_announcements = Announcement.objects.all().filter(nomcom=1)

    regimes = []

    for chair in old_chairs:
        chair_announcements = (nomcom_announcements.filter(nomcom_chair=chair).
                               order_by('-announced_date','-announced_time'))
        regimes = regimes + [{'chair': chair, 'announcements' : chair_announcements }]

    return render_to_response("announcements/nomcom.html", {
            'curr_chair_email' : curr_chair_email,
            'curr_chair_name' : curr_chair_name,
            'regimes' : regimes,
                                                  })
