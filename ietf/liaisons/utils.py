from ietf.idtracker.models import Area, IETFWG
from ietf.liaisons.models import SDOs
from ietf.liaisons.accounts import is_ietfchair, is_iabchair, is_iab_executive_director

IETFCHAIR = {'name': u'The IETF Chair', 'address': u'chair@ietf.org'}
IESG = {'name': u'The IESG', 'address': u'iesg@ietf.org'}
IAB = {'name': u'The IAB', 'address': u'iab@iab.org'}
IABCHAIR = {'name': u'The IAB Chair', 'address': u'iab-chair@iab.org'}
IABEXECUTIVEDIRECTOR = {'name': u'The IAB Executive Director', 'address': u'execd@iab.org'}


class FakePerson(object):

    def __init__(self, name, address):
        self.name = name
        self.address = address

    def email(self):
        return (self.name, self.address)


class Entity(object):

    poc = []
    cc = []

    def __init__(self, name, obj=None):
        self.name = name
        self.obj = obj

    def get_poc(self):
        if not isinstance(self.poc, list):
            return [self.poc]
        return self.poc

    def get_cc(self, person=None):
        if not isinstance(self.cc, list):
            return [self.cc]
        return self.cc

    def get_from_cc(self, person=None):
        return []


class IETFEntity(Entity):

    poc = FakePerson(**IETFCHAIR)
    cc = FakePerson(**IESG)

    def get_from_cc(self, person):
        result = []
        if not is_ietfchair(person):
            result.append(self.poc)
        result.append(self.cc)
        return result


class IABEntity(Entity):
    chair = FakePerson(**IABCHAIR)
    director = FakePerson(**IABEXECUTIVEDIRECTOR)
    poc = [chair, director]
    cc = FakePerson(**IAB)

    def get_from_cc(self, person):
        result = []
        if not is_iabchair(person):
            result.append(self.chair)
        result.append(self.cc)
        if not is_iab_executive_director(person):
            result.append(self.director)
        return result


class AreaEntity(Entity):

    def get_poc(self):
        return [i.person for i in self.obj.areadirector_set.all()]

    def get_cc(self, person=None):
        return [FakePerson(**IETFCHAIR)]

    def get_from_cc(self, person):
        result = [i.person for i in self.obj.areadirector_set.all() if i.person!=person]
        result.append(FakePerson(**IETFCHAIR))
        return result


class WGEntity(Entity):

    def get_poc(self):
        return [i.person for i in self.obj.wgchair_set.all()]

    def get_cc(self, person=None):
        result = [i.person for i in self.obj.area_directors()]
        if self.obj.email_address:
            result.append(FakePerson(name ='%s Discussion List' % self.obj.group_acronym.name,
                                     address = self.obj.email_address))
        return result

    def get_from_cc(self, person):
        result = [i.person for i in self.obj.wgchair_set.all() if i.person!=person]
        result += [i.person for i in self.obj.area_directors()]
        if self.obj.email_address:
            result.append(FakePerson(name ='%s Discussion List' % self.obj.group_acronym.name,
                                     address = self.obj.email_address))
        return result


class SDOEntity(Entity):

    def get_poc(self):
        return []

    def get_cc(self, person=None):
        manager = self.obj.liaisonmanager()
        if manager:
            return [manager.person]
        return []

    def get_from_cc(self, person=None):
        manager = self.obj.liaisonmanager()
        if manager and manager.person!=person:
            return [manager.person]
        return []


class EntityManager(object):

    def __init__(self, pk=None, name=None, queryset=None):
        self.pk = pk
        self.name = name
        self.queryset = queryset

    def get_entity(self, pk=None):
        return Entity(name=self.name)

    def get_managed_list(self):
        return [(self.pk, self.name)]

    def can_send_on_behalf(self, person):
        return []


class IETFEntityManager(EntityManager):

    def __init__(self, *args, **kwargs):
        super(IETFEntityManager, self).__init__(*args, **kwargs)
        self.entity = IETFEntity(name=self.name)

    def get_entity(self, pk=None):
        return self.entity

    def can_send_on_behalf(self, person):
        if is_ietfchair(person):
            return self.get_managed_list()
        return []


class IABEntityManager(EntityManager):

    def __init__(self, *args, **kwargs):
        super(IABEntityManager, self).__init__(*args, **kwargs)
        self.entity = IABEntity(name=self.name)

    def get_entity(self, pk=None):
        return self.entity

    def can_send_on_behalf(self, person):
        if (is_iabchair(person) or
            is_iab_executive_director(person)):
            return self.get_managed_list()
        return []


class AreaEntityManager(EntityManager):

    def __init__(self, pk=None, name=None, queryset=None):
        super(AreaEntityManager, self).__init__(pk, name, queryset)
        if self.queryset == None:
            self.queryset = Area.active_areas()

    def get_managed_list(self, query_filter=None):
        if not query_filter:
            query_filter = {}
        return [(u'%s_%s' % (self.pk, i.pk), i.area_acronym.name) for i in self.queryset.filter(**query_filter).order_by('area_acronym__name')]

    def get_entity(self, pk=None):
        if not pk:
            return None
        try:
            obj = self.queryset.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return None
        return AreaEntity(name=obj.area_acronym.name, obj=obj)

    def can_send_on_behalf(self, person):
        query_filter = {'areadirector__in': person.areadirector_set.all()}
        return self.get_managed_list(query_filter)


class WGEntityManager(EntityManager):

    def __init__(self, pk=None, name=None, queryset=None):
        super(WGEntityManager, self).__init__(pk, name, queryset)
        if self.queryset == None:
            self.queryset = IETFWG.objects.filter(group_type=1, status=IETFWG.ACTIVE, areagroup__area__status=Area.ACTIVE)

    def get_managed_list(self, query_filter=None):
        if not query_filter:
            query_filter = {}
        return [(u'%s_%s' % (self.pk, i.pk), i.group_acronym.name) for i in self.queryset.filter(**query_filter).order_by('group_acronym__name')]

    def get_entity(self, pk=None):
        if not pk:
            return None
        try:
            obj = self.queryset.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return None
        return WGEntity(name=obj.group_acronym.name, obj=obj)

    def can_send_on_behalf(self, person):
        wgs = set([i.group_acronym.pk for i in person.wgchair_set.all()])
        wgs = wgs.union([i.group_acronym.pk for i in person.wgsecretary_set.all()])
        query_filter = {'pk__in': wgs}
        return self.get_managed_list(query_filter)


class SDOEntityManager(EntityManager):

    def __init__(self, pk=None, name=None, queryset=None):
        super(SDOEntityManager, self).__init__(pk, name, queryset)
        if self.queryset == None:
            self.queryset = SDOs.objects.all()

    def get_managed_list(self):
        return [(u'%s_%s' % (self.pk, i.pk), i.sdo_name) for i in self.queryset.order_by('sdo_name')]

    def get_entity(self, pk=None):
        if not pk:
            return None
        try:
            obj = self.queryset.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return None
        return SDOEntity(name=obj.sdo_name, obj=obj)


class IETFHierarchyManager(object):

    def __init__(self):
        self.managers = {'ietf': IETFEntityManager(pk='ietf', name=u'The IETF'),
                         'iesg': IETFEntityManager(pk='iesg', name=u'The IESG'),
                         'iab': IABEntityManager(pk='iab', name=u'The IAB'),
                         'area': AreaEntityManager(pk='area', name=u'IETF Areas'),
                         'wg': WGEntityManager(pk='wg', name=u'IETF Working Groups'),
                         'sdo': SDOEntityManager(pk='sdo', name=u'Standards Development Organizations'),
                         'othersdo': EntityManager(pk='othersdo', name=u'Other SDOs'),
                        }

    def get_entity_by_key(self, entity_id):
        id_list = entity_id.split('_', 1)
        key = id_list[0]
        pk = None
        if len(id_list)==2:
            pk = id_list[1]
        if key not in self.managers.keys():
            return None
        return self.managers[key].get_entity(pk)

    def get_all_entities(self):
        entities = []
        for manager in self.managers.values():
            entities += manager.get_managed_list()
        return entities

    def get_all_incoming_entities(self):
        entities = []
        results = []
        for key in ['ietf', 'iesg', 'iab']:
            results += self.managers[key].get_managed_list()
        entities.append(('Main IETF Entities', results))
        entities.append(('IETF Areas', self.managers['area'].get_managed_list()))
        entities.append(('IETF Working Groups', self.managers['wg'].get_managed_list()))
        return entities

    def get_all_outgoing_entities(self):
        entities = [(self.managers['sdo'].name, self.managers['sdo'].get_managed_list())]
        entities += [(self.managers['othersdo'].name, self.managers['othersdo'].get_managed_list())]
        return entities

    def get_entities_for_person(self, person):
        entities = []
        results = []
        for key in ['ietf', 'iesg', 'iab']:
            results += self.managers[key].can_send_on_behalf(person)
        if results:
            entities.append(('Main IETF Entities', results))
        areas = self.managers['area'].can_send_on_behalf(person)
        if areas:
            entities.append(('IETF Areas', areas))
        wgs = self.managers['wg'].can_send_on_behalf(person)
        if wgs:
            entities.append(('IETF Working Groups', wgs))
        return entities

IETFHM = IETFHierarchyManager()
