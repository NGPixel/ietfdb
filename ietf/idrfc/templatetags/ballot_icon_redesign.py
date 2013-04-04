# Copyright (C) 2009-2010 Nokia Corporation and/or its subsidiary(-ies).
# All rights reserved. Contact: Pasi Eronen <pasi.eronen@nokia.com>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above
#    copyright notice, this list of conditions and the following
#    disclaimer in the documentation and/or other materials provided
#    with the distribution.
#
#  * Neither the name of the Nokia Corporation and/or its
#    subsidiary(-ies) nor the names of its contributors may be used
#    to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime

from django import template
from django.core.urlresolvers import reverse as urlreverse
from django.conf import settings
from django.db.models import Q
from django.utils.safestring import mark_safe

from ietf.ietfauth.utils import user_is_person, has_role
from ietf.doc.models import BallotDocEvent, BallotPositionDocEvent, IESG_BALLOT_ACTIVE_STATES, IESG_SUBSTATE_TAGS


register = template.Library()

def render_ballot_icon(user, doc):
    if not doc:
        return ""

    # FIXME: temporary backwards-compatibility hack
    from ietf.doc.models import Document
    if not isinstance(doc, Document):
        doc = doc._draft

    if doc.type_id == "draft":
        if doc.get_state_slug("draft-iesg") not in IESG_BALLOT_ACTIVE_STATES:
            return ""
    elif doc.type_id == "charter":
        if doc.get_state_slug() not in ("intrev", "iesgrev"):
            return ""
    elif doc.type_id == "conflrev":
       if doc.get_state_slug() not in ("iesgeval","defer"):
           return ""

    ballot = doc.active_ballot()
    if not ballot:
        return ""

    def sort_key(t):
        _, pos = t
        if not pos:
            return (2, 0)
        elif pos.pos.blocking:
            return (0, pos.pos.order)
        else:
            return (1, pos.pos.order)

    positions = list(doc.active_ballot().active_ad_positions().items())
    positions.sort(key=sort_key)

    edit_position_url = ""
    if has_role(user, "Area Director"):
        edit_position_url = urlreverse('ietf.idrfc.views_ballot.edit_position', kwargs=dict(name=doc.name, ballot_id=ballot.pk))

    title = "IESG positions (click to show more%s)" % (", right-click to edit position" if edit_position_url else "")

    res = ['<a href="%s" data-popup="%s" data-edit="%s" title="%s" class="ballot-icon"><table>' % (
            urlreverse("doc_ballot", kwargs=dict(name=doc.name, ballot_id=ballot.pk)),
            urlreverse("ietf.doc.views_doc.ballot_popup", kwargs=dict(name=doc.name, ballot_id=ballot.pk)),
            edit_position_url,
            title
            )]

    res.append("<tr>")

    for i, (ad, pos) in enumerate(positions):
        if i > 0 and i % 5 == 0:
            res.append("</tr>")
            res.append("<tr>")

        c = "position-%s" % (pos.pos.slug if pos else "norecord")

        if user_is_person(user, ad):
            c += " my"

        res.append('<td class="%s" />' % c)

    res.append("</tr>")
    res.append("</table></a>")

    return "".join(res)

class BallotIconNode(template.Node):
    def __init__(self, doc_var):
        self.doc_var = doc_var
    def render(self, context):
        doc = template.resolve_variable(self.doc_var, context)
        return render_ballot_icon(context.get("user"), doc)

def do_ballot_icon(parser, token):
    try:
        tag_name, doc_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires exactly two arguments" % token.contents.split()[0]
    return BallotIconNode(doc_name)

register.tag('ballot_icon', do_ballot_icon)


@register.filter
def my_position(doc, user):
    if not has_role(user, "Area Director"):
        return None
    # FIXME: temporary backwards-compatibility hack
    from ietf.doc.models import Document
    if not isinstance(doc, Document):
        doc = doc._draft

    ballot = doc.active_ballot()
    pos = "No Record"
    if ballot:
        changed_pos = doc.latest_event(BallotPositionDocEvent, type="changed_ballot_position", ad__user=user, ballot=ballot)
        if changed_pos:
            pos = changed_pos.pos.name;
    return pos

@register.filter()
def state_age_colored(doc):
    # FIXME: temporary backwards-compatibility hack
    from ietf.doc.models import Document
    if not isinstance(doc, Document):
        doc = doc._draft

    if doc.type_id == 'draft':
        if not doc.get_state_slug() in ["active", "rfc"]:
            # Don't show anything for expired/withdrawn/replaced drafts
            return ""
        main_state = doc.get_state_slug('draft-iesg')
        if not main_state:
            return ""

        if main_state in ["dead", "watching", "pub"]:
            return ""
        try:
            state_date = doc.docevent_set.filter(
                              Q(desc__istartswith="Draft Added by ")|
                              Q(desc__istartswith="Draft Added in state ")|
                              Q(desc__istartswith="Draft added in state ")|
                              Q(desc__istartswith="State changed to ")|
                              Q(desc__istartswith="State Changes to ")|
                              Q(desc__istartswith="Sub state has been changed to ")|
                              Q(desc__istartswith="State has been changed to ")|
                              Q(desc__istartswith="IESG has approved and state has been changed to")|
                              Q(desc__istartswith="IESG process started in state")
                          ).order_by('-time')[0].time.date() 
        except IndexError:
            state_date = datetime.date(1990,1,1)
        days = (datetime.date.today() - state_date).days
        # loosely based on 
        # http://trac.tools.ietf.org/group/iesg/trac/wiki/PublishPath
        if main_state == "lc":
            goal1 = 30
            goal2 = 30
        elif main_state == "rfcqueue":
            goal1 = 60
            goal2 = 120
        elif main_state in ["lc-req", "ann"]:
            goal1 = 4
            goal2 = 7
        elif 'need-rev' in [x.slug for x in doc.tags.all()]:
            goal1 = 14
            goal2 = 28
        elif main_state == "pub-req":
            goal1 = 7
            goal2 = 14
        elif main_state == "ad-eval":
            goal1 = 14
            goal2 = 28
        else:
            goal1 = 14
            goal2 = 28
        if days > goal2:
            class_name = "ietf-small ietf-highlight-r"
        elif days > goal1:
            class_name = "ietf-small ietf-highlight-y"
        else:
            class_name = "ietf-small"
        if days > goal1:
            title = ' title="Goal is &lt;%d days"' % (goal1,)
        else:
            title = ''
        return mark_safe('<span class="%s"%s>(for&nbsp;%d&nbsp;day%s)</span>' % (
                class_name, title, days, 's' if days != 1 else ''))
    else:
        return ""
