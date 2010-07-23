from ietf.idtracker.models import Area, IETFWG
from ietf.liaisons.models import SDOs

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


class IETFEntity(object):

    def __init__(self, name, poc=None, obj=None, cc=None):
        self.name = name
        self.poc = poc
        self.cc = cc
        self.obj = obj

    def get_poc(self):
        if not isinstance(self.poc, list):
            return [self.poc]
        return self.poc

    def get_cc(self, person=None):
        if not isinstance(self.cc, list):
            return [self.cc]
        return self.cc


class AreaEntity(IETFEntity):

    def get_poc(self):
        return [i.person for i in self.obj.areadirector_set.all()]

    def get_cc(self, person=None):
        return [FakePerson(**IETFCHAIR)]


class WGEntity(IETFEntity):

    def get_poc(self):
        return [i.person for i in self.obj.wgchair_set.all()]

    def get_cc(self, person=None):
        result = [i.person for i in self.obj.area_directors()]
        if self.obj.email_address:
            result.append(FakePerson(name ='%s Discussion List' % self.obj.group_acronym.name,
                                     address = self.obj.email_address))
        return result


class SDOEntity(IETFEntity):

    def get_poc(self):
        return []

    def get_cc(self, person=None):
        return []

    def get_from_cc(self, person=None):
        manager = self.obj.liaisonmanager()
        if manager and manager.person!=person:
            return [manager.person]
        return []


class IETFEntityManager(object):

    def __init__(self, pk=None, name=None, queryset=None, poc=None, cc=None):
        self.pk = pk
        self.name = name
        self.queryset = queryset
        self.poc = poc
        self.cc = cc

    def get_entity(self, pk=None):
        return IETFEntity(name=self.name, poc=self.poc, cc=self.cc)

    def get_managed_list(self):
        return [(self.pk, self.name)]


class AreaEntityManager(IETFEntityManager):

    def __init__(self, pk=None, name=None, queryset=None, poc=None):
        super(AreaEntityManager, self).__init__(pk, name, queryset, poc)
        if self.queryset == None:
            self.queryset = Area.active_areas()

    def get_managed_list(self):
        return [(u'%s_%s' % (self.pk, i.pk), i.area_acronym.name) for i in self.queryset.order_by('area_acronym__name')]

    def get_entity(self, pk=None):
        if not pk:
            return None
        try:
            obj = self.queryset.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return None
        return AreaEntity(name=obj.area_acronym.name, obj=obj)


class WGEntityManager(IETFEntityManager):

    def __init__(self, pk=None, name=None, queryset=None, poc=None):
        super(WGEntityManager, self).__init__(pk, name, queryset, poc)
        if self.queryset == None:
            self.queryset = IETFWG.objects.filter(group_type=1, status=IETFWG.ACTIVE, areagroup__area__status=Area.ACTIVE)

    def get_managed_list(self):
        return [(u'%s_%s' % (self.pk, i.pk), i.group_acronym.name) for i in self.queryset.order_by('group_acronym__name')]

    def get_entity(self, pk=None):
        if not pk:
            return None
        try:
            obj = self.queryset.get(pk=pk)
        except self.queryset.model.DoesNotExist:
            return None
        return WGEntity(name=obj.group_acronym.name, obj=obj)


class SDOEntityManager(IETFEntityManager):

    def __init__(self, pk=None, name=None, queryset=None, poc=None):
        super(SDOEntityManager, self).__init__(pk, name, queryset, poc)
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
        self.managers = {'ietf': IETFEntityManager(pk='ietf', name=u'The IETF',
                                                   poc=FakePerson(**IETFCHAIR),
                                                   cc=FakePerson(**IESG)),
                         'iesg': IETFEntityManager(pk='iesg', name=u'The IESG',
                                                   poc=FakePerson(**IETFCHAIR),
                                                   cc=FakePerson(**IESG)),
                         'iab': IETFEntityManager(pk='iab', name=u'The IAB',
                                                  poc=[FakePerson(**IABCHAIR),
                                                       FakePerson(**IABEXECUTIVEDIRECTOR)],
                                                  cc=FakePerson(**IAB)),
                         'area': AreaEntityManager(pk='area', name=u'IETF Areas'),
                         'wg': WGEntityManager(pk='wg', name=u'IETF Working Groups'),
                         'sdo': SDOEntityManager(pk='sdo', name=u'Standards Development Organizations'),
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
        entities = [(self.manager['sdo'].name, self.managers['sdo'].get_managed_list())]
        return entities

IETFHM = IETFHierarchyManager()
