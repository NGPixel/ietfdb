from redesign.person.models import Person
from redesign.group.models import Role


LIAISON_EDIT_GROUPS = ['Secretariat']


def get_ietf_chair():
    try:
        return Person.objects.get(email__role__name="chair", email__role__group__acronym="ietf")
    except Person.DoesNotExist:
        return None


def get_iesg_chair():
    return get_ietf_chair()


def get_iab_chair():
    try:
        return Person.objects.get(email__role__name="chair", email__role__group__acronym="iab")
    except Person.DoesNotExist:
        return None


def get_iab_executive_director():
    try:
        return Person.objects.get(email__role__name="execdir", email__role__group__acronym="iab")
    except Person.DoesNotExist:
        return None


def get_person_for_user(user):
    return user.get_profile()


def is_areadirector(person):
    return bool(Role.objects.filter(email__person=person, name="ad", group__state="active", group__type="area"))


def is_wgchair(person):
    return bool(Role.objects.filter(email__person=person, name="chair", group__state="active", group__type="wg"))


def is_wgsecretary(person):
    return bool(Role.objects.filter(email__person=person, name="sec", group__state="active", group__type="wg"))


def is_ietfchair(person):
    return bool(Role.objects.filter(email__person=person, name="chair", group__acronym="ietf"))


def is_iabchair(person):
    return bool(Role.objects.filter(email__person=person, name="chair", group__acronym="iab"))


def is_iab_executive_director(person):
    return bool(Role.objects.filter(email__person=person, name="execdir", group__acronym="iab"))


def can_add_outgoing_liaison(user):
    person = get_person_for_user(user)
    if not person:
        return False

    if (is_areadirector(person) or is_wgchair(person) or
        is_wgsecretary(person) or is_ietfchair(person) or
        is_iabchair(person) or is_iab_executive_director(person) or
        is_sdo_liaison_manager(person) or is_secretariat(user)):
        return True
    return False


def is_sdo_liaison_manager(person):
    return bool(Role.objects.filter(email__person=person, name="liaiman", group__type="sdo"))


def is_sdo_authorized_individual(person):
    return bool(Role.objects.filter(email__person=person, name="auth", group__type="sdo"))


def is_secretariat(user):
    return bool(Role.objects.filter(email__person=user.get_profile(), name="auth", group__acronym="secretariat"))


def can_add_incoming_liaison(user):
    person = get_person_for_user(user)
    if not person:
        return False

    if (is_sdo_liaison_manager(person) or
        is_sdo_authorized_individual(person) or
        is_secretariat(user)):
        return True
    return False


def can_add_liaison(user):
    return can_add_incoming_liaison(user) or can_add_outgoing_liaison(user)


def is_sdo_manager_for_outgoing_liaison(person, liaison):
    if liaison.from_group and liaison.from_group.type_id == "sdo":
        return bool(liaison.from_group.role_set.filter(name="liaiman", email__person=person))
    return False


def is_sdo_manager_for_incoming_liaison(person, liaison):
    if liaison.to_group and liaison.to_group.type_id == "sdo":
        return bool(liaison.to_group.role_set.filter(name="liaiman", email__person=person))
    return False


def can_edit_liaison(user, liaison):
    if is_secretariat(user):
        return True
    person = get_person_for_user(user)
    if is_sdo_liaison_manager(person):
        return (is_sdo_manager_for_outgoing_liaison(person, liaison) or
                is_sdo_manager_for_incoming_liaison(person, liaison))
    return False
