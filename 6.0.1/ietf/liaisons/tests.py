import datetime, os, shutil
import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse as urlreverse
from django.db.models import Q
from StringIO import StringIO
from pyquery import PyQuery

from ietf.utils.test_utils import TestCase, login_testing_unauthorized
from ietf.utils.test_data import make_test_data, create_person
from ietf.utils.mail import outbox

from ietf.liaisons.models import (LiaisonStatement, LiaisonStatementPurposeName,
    LiaisonStatementState, LiaisonStatementEvent)
from ietf.person.models import Person, Email
from ietf.group.models import Group, Role
from ietf.liaisons.mails import send_sdo_reminder, possibly_send_deadline_reminder

# -------------------------------------------------
# Helper Functions
# -------------------------------------------------

def make_liaison_models():
    sdo = Group.objects.create(
        name="United League of Marsmen",
        acronym="ulm",
        state_id="active",
        type_id="sdo",
        )
    sdo2 = Group.objects.create(
        name="Standards Development Organization",
        acronym="sdo",
        state_id="active",
        type_id="sdo",
        )
        
    # liaison manager
    create_person(sdo, 'liaiman')
    create_person(sdo, 'auth')

    mars_group = Group.objects.get(acronym="mars")
    create_person(mars_group, 'secr')
    create_person(Group.objects.get(acronym='iab'), "execdir")
    
    s = LiaisonStatement.objects.create(
        title="Comment from United League of Marsmen",
        purpose_id="comment",
        body="The recently proposed Martian Standard for Communication Links neglects the special ferro-magnetic conditions of the Martian soil.",
        deadline=datetime.date.today() + datetime.timedelta(days=7),
        #from_name=sdo.name,
        from_contact=Email.objects.last(),
        #to_name=mars_group.name,
        to_contacts="%s@ietf.org" % mars_group.acronym,
        state_id='approved',
        )
    s.from_groups.add(sdo)
    s.to_groups.add(mars_group)
    
    # create events
    e = LiaisonStatementEvent.objects.create(
        type_id='submitted',
        by=Person.objects.get(name='Ulm Liaiman'),
        statement=s,
        desc='Statement Submitted'
    )
        
    return s
    
def get_liaison_post_data(type='incoming'):
    '''Return a dictionary containing basic liaison entry data'''
    if type == 'incoming':
        from_group = Group.objects.get(acronym='ulm')
        to_group = Group.objects.get(acronym="mars")
    else:
        to_group = Group.objects.get(acronym='ulm')
        from_group = Group.objects.get(acronym="mars")

    return dict(from_groups=str(from_group.pk),
                from_contact='from_contact@example.com',
                to_groups=str(to_group.pk),
                to_contacts='to_contacts@example.com',
                purpose="info",
                title="title",
                submitted_date=datetime.datetime.today().strftime("%Y-%m-%d"),
                body="body",
                send="1" )

# -------------------------------------------------
# Test Classes
# -------------------------------------------------

class LiaisonTests(TestCase):
    def test_overview(self):
        make_test_data()
        liaison = make_liaison_models()

        r = self.client.get(urlreverse('liaison_list'))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

    def test_details(self):
        make_test_data()
        liaison = make_liaison_models()

        r = self.client.get(urlreverse("liaison_detail", kwargs={ 'object_id': liaison.pk }))
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

    def test_feeds(self):
        make_test_data()
        liaison = make_liaison_models()

        r = self.client.get('/feed/liaison/recent/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

        r = self.client.get('/feed/liaison/from/%s/' % liaison.from_groups.first().acronym)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

        r = self.client.get('/feed/liaison/to/%s/' % liaison.to_groups.first().acronym)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

        r = self.client.get('/feed/liaison/subject/marsmen/')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

    def test_sitemap(self):
        make_test_data()
        liaison = make_liaison_models()

        r = self.client.get('/sitemap-liaison.xml')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(urlreverse("liaison_detail", kwargs={ 'object_id': liaison.pk }) in r.content)

    def test_help_pages(self):
        self.assertEqual(self.client.get('/liaison/help/').status_code, 200)
        self.assertEqual(self.client.get('/liaison/help/fields/').status_code, 200)
        self.assertEqual(self.client.get('/liaison/help/from_ietf/').status_code, 200)
        self.assertEqual(self.client.get('/liaison/help/to_ietf/').status_code, 200)


class LiaisonManagementTests(TestCase):
    def setUp(self):
        self.liaison_dir = os.path.abspath("tmp-liaison-dir")
        if not os.path.exists(self.liaison_dir):
            os.mkdir(self.liaison_dir)
        settings.LIAISON_ATTACH_PATH = self.liaison_dir

    def tearDown(self):
        shutil.rmtree(self.liaison_dir)

    def test_ajax(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('ajax_get_liaison_info') + "?to_groups=&from_groups="
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.content)
        self.assertEqual(data["error"], False)
        self.assertEqual(data["post_only"], False)
        self.assertTrue('cc' in data)
        self.assertTrue('needs_approval' in data)
        
        
    def test_add_restrictions(self):
        make_test_data()
        liaison = make_liaison_models()
        
        # incoming restrictions
        url = urlreverse('add_liaison') + "?incoming=1"
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        #q = PyQuery(r.content)
        #self.assertEqual(len(q('form textarea[name=body]')), 1)
        
    def test_taken_care_of(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('liaison_detail', kwargs=dict(object_id=liaison.pk))
        # normal get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form input[name=do_action_taken]')), 0)
        
        # log in and get
        self.client.login(username="secretary", password="secretary+password")

        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form input[name=do_action_taken]')), 1)
        
        # mark action taken
        r = self.client.post(url, dict(do_action_taken="1"))
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form input[name=do_action_taken]')), 0)
        liaison = LiaisonStatement.objects.get(id=liaison.id)
        self.assertTrue(liaison.action_taken)

    def test_obtained_approval(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('add_liaison')
        login_testing_unauthorized(self, "ad", url)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue('id_approved' in r.content)
        
    def test_approval_process(self):
        make_test_data()
        liaison = make_liaison_models()
        # has to come from WG to need approval
        liaison.from_groups.clear()
        liaison.from_groups.add(Group.objects.get(acronym="mars"))
        liaison.state=LiaisonStatementState.objects.get(slug='pending')
        liaison.save()

        # check the overview page
        url = urlreverse('liaison_approval_list')
        # this liaison is for a WG so we need the AD for the area
        login_testing_unauthorized(self, "ad", url)
        
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)

        # check detail page
        url = urlreverse('liaison_approval_detail', kwargs=dict(object_id=liaison.pk))
        self.client.logout()
        login_testing_unauthorized(self, "ad", url)

        # normal get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(liaison.title in r.content)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form input[name=approved]')), 1)

        # approve
        mailbox_before = len(outbox)
        r = self.client.post(url, dict(approved="1"))
        self.assertEqual(r.status_code, 302)

        liaison = LiaisonStatement.objects.get(id=liaison.id)
        self.assertTrue(liaison.approved)
        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue("Liaison Statement" in outbox[-1]["Subject"])

    def test_edit_liaison(self):
        make_test_data()
        liaison = make_liaison_models()
        from_group = liaison.from_groups.first()
        to_group = liaison.to_groups.first()
        
        url = urlreverse('liaison_edit', kwargs=dict(object_id=liaison.pk))
        login_testing_unauthorized(self, "secretary", url)

        # get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form input[name=from_contact]')), 1)

        # edit
        attachments_before = liaison.attachments.count()
        test_file = StringIO("hello world")
        test_file.name = "unnamed"
        r = self.client.post(url,
                             dict(from_groups=str(from_group.pk),
                                  from_contact=liaison.from_contact,
                                  to_groups=str(to_group.pk),
                                  to_contacts="to_poc@example.com",
                                  technical_contacts="technical_contact@example.com",
                                  cc_contacts="cc@example.com",
                                  purpose="action",
                                  deadline=(liaison.deadline + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                                  title="title",
                                  submitted_date=(liaison.submitted + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                                  body="body",
                                  attach_file_1=test_file,
                                  attach_title_1="attachment",
                                  ))
        self.assertEqual(r.status_code, 302)
        
        new_liaison = LiaisonStatement.objects.get(id=liaison.id)
        self.assertEqual(new_liaison.from_groups.first(), from_group)
        self.assertEqual(new_liaison.to_groups.first(), to_group)
        #self.assertEqual(new_liaison.to_contacts, "to_poc@example.com")
        #self.assertEqual(new_liaison.response_contacts, "responce_contact@example.com")
        self.assertEqual(new_liaison.technical_contacts, "technical_contact@example.com")
        self.assertEqual(new_liaison.cc_contacts, "cc@example.com")
        self.assertEqual(new_liaison.purpose, LiaisonStatementPurposeName.objects.get(slug='action'))
        self.assertEqual(new_liaison.deadline, liaison.deadline + datetime.timedelta(days=1)),
        self.assertEqual(new_liaison.title, "title")
        #self.assertEqual(new_liaison.submitted.date(), (liaison.submitted + datetime.timedelta(days=1)).date())
        self.assertEqual(new_liaison.body, "body")
        
        self.assertEqual(new_liaison.attachments.count(), attachments_before + 1)
        attachment = new_liaison.attachments.order_by("-name")[0]
        self.assertEqual(attachment.title, "attachment")
        with open(os.path.join(self.liaison_dir, attachment.external_url)) as f:
            written_content = f.read()

        test_file.seek(0)
        self.assertEqual(written_content, test_file.read())

    def test_incoming_access(self):
        '''Ensure only Secretariat, Liaison Managers, and Authorized Individuals
        have access to incoming liaisons.
        TODO: is it better to test the underlying function, and not look for button?
        '''
        make_test_data()
        liaison = make_liaison_models()
        url = urlreverse('liaison_list')
        
        # public user no access
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New incoming liaison')")), 0)
        
        # regular Chair no access
        self.client.login(username="marschairman", password="marschairman+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New incoming liaison')")), 0)
        
        # Liaison Manager has access
        self.client.login(username="ulm-liaiman", password="ulm-liaiman+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('a.btn:contains("New incoming liaison")')), 1)
        
        # Authorized Individual has access
        self.client.login(username="ulm-auth", password="ulm-auth+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New incoming liaison')")), 1)
        
        # Secretariat has access
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New incoming liaison')")), 1)
        
    def test_outgoing_access(self):
        make_test_data()
        liaison = make_liaison_models()
        url = urlreverse('liaison_list')
        
        # public user no access
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 0)
        
        # AD has access
        self.client.login(username="ad", password="ad+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # WG Chair has access
        self.client.login(username="marschairman", password="marschairman+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # WG Secretary has access
        self.client.login(username="mars-secr", password="mars-secr+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # IETF Chair has access
        self.client.login(username="ietf-chair", password="ietf-chair+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # IAB Chair has access
        self.client.login(username="iab-chair", password="iab-chair+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # IAB Executive Director
        self.client.login(username="iab-execdir", password="iab-execdir+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
        # Liaison Manager has access
        self.client.login(username="ulm-liaiman", password="ulm-liaiman+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('a.btn:contains("New outgoing liaison")')), 1)
        
        # Authorized Individual has no access
        self.client.login(username="ulm-auth", password="ulm-auth+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 0)
        
        # Secretariat has access
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q("a.btn:contains('New outgoing liaison')")), 1)
        
    def test_incoming_options(self):
        '''Check from_groups, to_groups options for different user classes'''
        make_test_data()
        liaison = make_liaison_models()
        url = urlreverse('add_liaison') + "?incoming=1"
        
        # get count of all IETF entities for to_group options
        top = Q(acronym__in=('ietf','iesg','iab'))
        areas = Q(type_id='area',state='active')
        wgs = Q(type_id='wg',state='active')
        all_entity_count = Group.objects.filter(top|areas|wgs).count()
        
        # Regular user
        # from_groups = groups for which they are Liaison Manager or Authorized Individual
        # to_groups = all IETF entities
        login_testing_unauthorized(self, "ulm-liaiman", url)
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('select#id_from_groups option')), 1)
        self.assertEqual(len(q('select#id_to_groups option')), all_entity_count)
        
        # Secretariat
        # from_groups = all active SDOs
        # to_groups = all IETF entities
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        all_sdos = Group.objects.filter(type_id='sdo',state='active').count()
        self.assertEqual(len(q('select#id_from_groups option')), all_sdos)
        self.assertEqual(len(q('select#id_to_groups option')), all_entity_count)
        
    def test_outgoing_options(self):
        make_test_data()
        liaison = make_liaison_models()
        url = urlreverse('add_liaison')
        
        # get count of all IETF entities for to_group options
        top = Q(acronym__in=('ietf','iesg','iab'))
        areas = Q(type_id='area',state='active')
        wgs = Q(type_id='wg',state='active')
        all_entity_count = Group.objects.filter(top|areas|wgs).count()
        
        # Regular user (Chair, AD)
        # from_groups = limited by role
        # to_groups = all SDOs
        person = Person.objects.filter(role__name='chair',role__group__acronym='mars').first()
        self.client.login(username="marschairman", password="marschairman+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        groups = Group.objects.filter(role__person=person,role__name='chair',state='active',type='wg')
        all_sdos = Group.objects.filter(state='active',type='sdo')
        self.assertEqual(len(q('select#id_from_groups option')), groups.count())
        self.assertEqual(len(q('select#id_to_groups option')), all_sdos.count())
        
        # Liaison Manager
        # from_groups = 
        # to_groups = limited to managed group
        
        # Secretariat
        # from_groups = all IETF entities
        # to_groups = all active SDOs
        self.client.login(username="secretary", password="secretary+password")
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        all_sdos = Group.objects.filter(type_id='sdo',state='active').count()
        self.assertEqual(len(q('select#id_from_groups option')), all_entity_count)
        self.assertEqual(len(q('select#id_to_groups option')), all_sdos)
        
        
    def test_add_incoming_liaison(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('add_liaison') + "?incoming=1"
        login_testing_unauthorized(self, "secretary", url)

        # get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form textarea[name=body]')), 1)

        # add new
        mailbox_before = len(outbox)
        test_file = StringIO("hello world")
        test_file.name = "unnamed"
        from_group = Group.objects.filter(type="sdo")[0]
        to_group = Group.objects.get(acronym="mars")
        submitter = Person.objects.get(user__username="marschairman")
        today = datetime.date.today()
        related_liaison = liaison
        r = self.client.post(url,
                             dict(from_groups=str(from_group.pk),
                                  from_contact=submitter.email_address(),
                                  to_groups=str(to_group.pk),
                                  to_contacts='to_contacts@example.com',
                                  technical_contacts="technical_contact@example.com",
                                  cc_contacts="cc@example.com",
                                  purpose="action",
                                  deadline=(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                                  related_to=str(related_liaison.pk),
                                  title="title",
                                  submitted_date=today.strftime("%Y-%m-%d"),
                                  body="body",
                                  attach_file_1=test_file,
                                  attach_title_1="attachment",
                                  send="1",
                                  ))
        #print r.content
        self.assertEqual(r.status_code, 302)
        
        l = LiaisonStatement.objects.all().order_by("-id")[0]
        self.assertSequenceEqual(l.from_groups.all(),[from_group])
        self.assertEqual(l.from_contact.address, submitter.email_address())
        self.assertSequenceEqual(l.to_groups.all(),[to_group])
        self.assertEqual(l.technical_contacts, "technical_contact@example.com")
        self.assertEqual(l.cc_contacts, "cc@example.com")
        self.assertEqual(l.purpose, LiaisonStatementPurposeName.objects.get(slug='action'))
        self.assertEqual(l.deadline, today + datetime.timedelta(days=1)),
        self.assertEqual(l.source_of_set.first().target,liaison),
        self.assertEqual(l.title, "title")
        self.assertEqual(l.submitted.date(), today)
        self.assertEqual(l.body, "body")
        self.assertEqual(l.state.slug, 'approved')
        
        self.assertEqual(l.attachments.count(), 1)
        attachment = l.attachments.all()[0]
        self.assertEqual(attachment.title, "attachment")
        with open(os.path.join(self.liaison_dir, attachment.external_url)) as f:
            written_content = f.read()

        test_file.seek(0)
        self.assertEqual(written_content, test_file.read())

        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue("Liaison Statement" in outbox[-1]["Subject"])
        
    def test_add_outgoing_liaison(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('add_liaison')
        login_testing_unauthorized(self, "secretary", url)

        # get
        r = self.client.get(url)
        self.assertEqual(r.status_code, 200)
        q = PyQuery(r.content)
        self.assertEqual(len(q('form textarea[name=body]')), 1)

        # add new
        mailbox_before = len(outbox)
        test_file = StringIO("hello world")
        test_file.name = "unnamed"
        from_group = Group.objects.get(acronym="mars")
        to_group = Group.objects.filter(type="sdo")[0]
        submitter = Person.objects.get(user__username="marschairman")
        today = datetime.date.today()
        related_liaison = liaison
        r = self.client.post(url,
                             dict(from_groups=str(from_group.pk),
                                  from_contact=submitter.email_address(),
                                  to_groups=str(to_group.pk),
                                  to_contacts='to_contacts@example.com',
                                  approved="",
                                  technical_contacts="technical_contact@example.com",
                                  cc_contacts="cc@example.com",
                                  purpose="action",
                                  deadline=(today + datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
                                  related_to=str(related_liaison.pk),
                                  title="title",
                                  submitted_date=today.strftime("%Y-%m-%d"),
                                  body="body",
                                  attach_file_1=test_file,
                                  attach_title_1="attachment",
                                  send="1",
                                  ))
        self.assertEqual(r.status_code, 302)
        
        l = LiaisonStatement.objects.all().order_by("-id")[0]
        self.assertSequenceEqual(l.from_groups.all(), [from_group])
        self.assertEqual(l.from_contact.address, submitter.email_address())
        self.assertSequenceEqual(l.to_groups.all(), [to_group])
        self.assertEqual(l.to_contacts, "to_contacts@example.com")
        self.assertEqual(l.technical_contacts, "technical_contact@example.com")
        self.assertEqual(l.cc_contacts, "cc@example.com")
        self.assertEqual(l.purpose, LiaisonStatementPurposeName.objects.get(slug='action'))
        self.assertEqual(l.deadline, today + datetime.timedelta(days=1)),
        self.assertEqual(l.source_of_set.first().target,liaison),
        self.assertEqual(l.title, "title")
        self.assertEqual(l.submitted.date(), today)
        self.assertEqual(l.body, "body")
        self.assertEqual(l.state.slug,'pending')
        
        self.assertEqual(l.attachments.count(), 1)
        attachment = l.attachments.all()[0]
        self.assertEqual(attachment.title, "attachment")
        with open(os.path.join(self.liaison_dir, attachment.external_url)) as f:
            written_content = f.read()

        test_file.seek(0)
        self.assertEqual(written_content, test_file.read())

        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue("Liaison Statement" in outbox[-1]["Subject"])

    # -------------------------------------------------
    # Form validations
    # -------------------------------------------------
    def test_post_and_send_fail(self):
        make_test_data()
        liaison = make_liaison_models()
        
        url = urlreverse('add_liaison') + "?incoming=1"
        login_testing_unauthorized(self, "ulm-liaiman", url)
        
        r = self.client.post(url,get_liaison_post_data(),follow=True)
        
        self.assertEqual(r.status_code, 200)
        self.assertTrue('As an IETF Liaison Manager you can not send incoming liaison statements' in r.content)
    
    def test_deadline_field(self):
        '''Required for action, comment, not info, response'''
        pass
        
    def test_email_validations(self):
        make_test_data()
        make_liaison_models()
        
        url = urlreverse('add_liaison') + "?incoming=1"
        login_testing_unauthorized(self, "secretary", url)
        
        post_data = get_liaison_post_data()
        post_data['from_contact'] = 'bademail'
        post_data['to_contacts'] = 'bademail'
        post_data['technical_contacts'] = 'bad_email'
        post_data['action_holder_contacts'] = 'bad_email'
        post_data['cc_contacts'] = 'bad_email'
        r = self.client.post(url,post_data,follow=True)
        
        q = PyQuery(r.content)
        self.assertEqual(r.status_code, 200)
        result = q('#id_technical_contacts').parent().parent('.has-error')
        result = q('#id_action_holder_contacts').parent().parent('.has-error')
        result = q('#id_cc_contacts').parent().parent('.has-error')
        self.assertEqual(len(result), 1)
        
    def test_body_or_attachment(self):
        make_test_data()
        make_liaison_models()
        
        url = urlreverse('add_liaison') + "?incoming=1"
        login_testing_unauthorized(self, "secretary", url)
        
        post_data = get_liaison_post_data()
        post_data['body'] = ''
        r = self.client.post(url,post_data,follow=True)
        
        self.assertEqual(r.status_code, 200)
        self.assertTrue('You must provide a body or attachment files' in r.content)
        
    def test_send_sdo_reminder(self):
        make_test_data()
        make_liaison_models()

        mailbox_before = len(outbox)
        send_sdo_reminder(Group.objects.filter(type="sdo")[0])
        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue("authorized individuals" in outbox[-1]["Subject"])

    def test_send_liaison_deadline_reminder(self):
        make_test_data()
        liaison = make_liaison_models()

        mailbox_before = len(outbox)
        possibly_send_deadline_reminder(liaison)
        self.assertEqual(len(outbox), mailbox_before + 1)
        self.assertTrue("deadline" in outbox[-1]["Subject"])

        # try pushing the deadline
        liaison.deadline = liaison.deadline + datetime.timedelta(days=30)
        liaison.save()
        
        mailbox_before = len(outbox)
        possibly_send_deadline_reminder(liaison)
        self.assertEqual(len(outbox), mailbox_before)
