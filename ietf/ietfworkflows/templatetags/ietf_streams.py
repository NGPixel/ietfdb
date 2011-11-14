from django import template
from django.conf import settings
from django.core.urlresolvers import reverse as urlreverse

from ietf.idrfc.idrfc_wrapper import IdRfcWrapper, IdWrapper
from ietf.ietfworkflows.utils import (get_workflow_for_draft,
                                      get_state_for_draft)
from ietf.wgchairs.accounts import (can_manage_shepherd_of_a_document,
                                    can_manage_writeup_of_a_document)
from ietf.ietfworkflows.streams import get_stream_from_wrapper
from ietf.ietfworkflows.accounts import (can_edit_state, can_edit_stream, can_adopt)

register = template.Library()


@register.inclusion_tag('ietfworkflows/stream_state.html', takes_context=True)
def stream_state(context, doc):
    request = context.get('request', None)
    data = {}
    stream = get_stream_from_wrapper(doc)
    data.update({'stream': stream})
    if not stream:
        return data

    idwrapper = None
    if isinstance(doc, IdRfcWrapper):
        idwrapper = doc.id
    elif isinstance(doc, IdWrapper):
        idwrapper = doc
    if not idwrapper:
        return data

    draft = getattr(idwrapper, '_draft', None)
    if not draft:
        return data

    workflow = get_workflow_for_draft(draft)
    state = get_state_for_draft(draft)

    data.update({'workflow': workflow,
                 'draft': draft,
                 'state': state})

    return data


@register.inclusion_tag('ietfworkflows/workflow_history_entry.html', takes_context=True)
def workflow_history_entry(context, entry):
    real_entry = entry.get_real_instance()
    return {'entry': real_entry,
            'entry_class': real_entry.__class__.__name__.lower()}


@register.inclusion_tag('ietfworkflows/edit_actions.html', takes_context=True)
def edit_actions(context, wrapper):
    request = context.get('request', None)
    user = request and request.user
    if not user:
        return {}
    idwrapper = None
    if isinstance(wrapper, IdRfcWrapper):
        idwrapper = wrapper.id
    elif isinstance(wrapper, IdWrapper):
        idwrapper = wrapper
    if not idwrapper:
        return None
    draft = idwrapper._draft
    doc = wrapper
    possible_actions = [
        ("Adopt in WG", can_adopt(user, draft), urlreverse('edit_adopt', kwargs=dict(name=doc.draft_name))) if settings.USE_DB_REDESIGN_PROXY_CLASSES else ("", False, ""),
        ("Change stream state", can_edit_state(user, draft), urlreverse('edit_state', kwargs=dict(name=doc.draft_name))),
        ("Change stream", can_edit_stream(user, draft), urlreverse('edit_stream', kwargs=dict(name=doc.draft_name))),
        ("Change shepherd", can_manage_shepherd_of_a_document(user, draft), urlreverse('doc_managing_shepherd', kwargs=dict(acronym=draft.group.acronym, name=draft.filename))),
        ("Change stream writeup", can_manage_writeup_of_a_document(user, draft), urlreverse('doc_managing_writeup', kwargs=dict(acronym=draft.group.acronym, name=draft.filename))),
        ]
    return dict(actions=[(url, action_name) for action_name, active, url, in possible_actions if active])
