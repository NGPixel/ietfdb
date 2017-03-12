import debug                            # pyflakes:ignore
import os
import shutil

from django.conf import settings
from django.core.urlresolvers import reverse

from ietf.doc.models import Document
from ietf.group.models import Group
from ietf.meeting.models import Session, TimeSlot, SchedTimeSessAssignment
from ietf.meeting.test_data import make_meeting_test_data
from ietf.utils.test_data import make_test_data
from ietf.utils.test_utils import TestCase
from ietf.utils.mail import outbox

from ietf.name.models import SessionStatusName
from ietf.meeting.factories import SessionFactory

from ietf.secr.proceedings.proc_utils import (create_proceedings, import_audio_files,
    get_timeslot_for_filename, normalize_room_name, send_audio_import_warning,
    get_or_create_recording_document, create_recording, get_next_sequence)


SECR_USER='secretary'

class ProceedingsTestCase(TestCase):
    def test_main(self):
        "Main Test"
        make_test_data()
        url = reverse('ietf.secr.proceedings.views.main')
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        # test chair access
        self.client.logout()
        self.client.login(username="marschairman", password="marschairman+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

class RecordingTestCase(TestCase):
    def setUp(self):
        self.meeting_recordings_dir = os.path.abspath("tmp-meeting-recordings-dir")
        self.saved_meeting_recordings_dir = settings.MEETING_RECORDINGS_DIR
        settings.MEETING_RECORDINGS_DIR = self.meeting_recordings_dir
        if not os.path.exists(self.meeting_recordings_dir):
            os.makedirs(self.meeting_recordings_dir)

    def tearDown(self):
        shutil.rmtree(self.meeting_recordings_dir)
        settings.MEETING_RECORDINGS_DIR = self.saved_meeting_recordings_dir

    def test_page(self):
        meeting = make_meeting_test_data()
        url = reverse('ietf.secr.proceedings.views.recording', kwargs={'meeting_num':meeting.number})
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_post(self):
        meeting = make_meeting_test_data()
        group = Group.objects.get(acronym='mars')
        session = Session.objects.filter(meeting=meeting,group=group).first()
        # explicitly set to scheduled for this test
        status = SessionStatusName.objects.get(slug='sched')
        session.status = status
        session.save()
        url = reverse('ietf.secr.proceedings.views.recording', kwargs={'meeting_num':meeting.number})
        data = dict(group=group.acronym,external_url='http://youtube.com/xyz',session=session.pk)
        self.client.login(username="secretary", password="secretary+password")
        response = self.client.post(url,data,follow=True)
        self.assertEqual(response.status_code, 200)
        self.failUnless(group.acronym in response.content)
        
        # now test edit
        doc = session.materials.filter(type='recording').first()
        external_url = 'http://youtube.com/aaa'
        url = reverse('ietf.secr.proceedings.views.recording_edit', kwargs={'meeting_num':meeting.number,'name':doc.name})
        response = self.client.post(url,dict(external_url=external_url),follow=True)
        self.assertEqual(response.status_code, 200)
        self.failUnless(external_url in response.content)
            
    def test_import_audio_files(self):
        meeting = make_meeting_test_data()
        group = Group.objects.get(acronym='mars')
        session = Session.objects.filter(meeting=meeting,group=group).first()
        status = SessionStatusName.objects.get(slug='sched')
        session.status = status
        session.save()
        timeslot = session.official_timeslotassignment().timeslot
        self.create_audio_file_for_timeslot(timeslot)
        import_audio_files(meeting)
        self.assertEqual(session.materials.filter(type='recording').count(),1)

    def create_audio_file_for_timeslot(self, timeslot):
        filename = self.get_filename_for_timeslot(timeslot)
        path = os.path.join(settings.MEETING_RECORDINGS_DIR,'ietf' + timeslot.meeting.number,filename)
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        with open(path, "w") as f:
            f.write('dummy')

    def get_filename_for_timeslot(self, timeslot):
        '''Returns the filename of a session recording given timeslot'''
        return "{prefix}-{room}-{date}.mp3".format(
            prefix=timeslot.meeting.type.slug + timeslot.meeting.number,
            room=normalize_room_name(timeslot.location.name),
            date=timeslot.time.strftime('%Y%m%d-%H%M'))

    def test_import_audio_files_shared_timeslot(self):
        meeting = make_meeting_test_data()
        mars_session = Session.objects.filter(meeting=meeting,group__acronym='mars').first()
        ames_session = Session.objects.filter(meeting=meeting,group__acronym='ames').first()
        scheduled = SessionStatusName.objects.get(slug='sched')
        mars_session.status = scheduled
        mars_session.save()
        ames_session.status = scheduled
        ames_session.save()
        timeslot = mars_session.official_timeslotassignment().timeslot
        SchedTimeSessAssignment.objects.create(timeslot=timeslot,session=ames_session,schedule=meeting.agenda)
        self.create_audio_file_for_timeslot(timeslot)
        import_audio_files(meeting)
        doc = mars_session.materials.filter(type='recording').first()
        self.assertTrue(doc in ames_session.materials.all())
        self.assertTrue(doc.docalias_set.filter(name='recording-42-mars-1'))
        self.assertTrue(doc.docalias_set.filter(name='recording-42-ames-1'))

    def test_normalize_room_name(self):
        self.assertEqual(normalize_room_name('Test Room'),'testroom')
        self.assertEqual(normalize_room_name('Rome/Venice'), 'rome_venice')

    def test_get_timeslot_for_filename(self):
        meeting = make_meeting_test_data()
        timeslot = TimeSlot.objects.filter(meeting=meeting,type='session').first()
        name = self.get_filename_for_timeslot(timeslot)
        self.assertEqual(get_timeslot_for_filename(name),timeslot)

    def test_get_or_create_recording_document(self):
        meeting = make_meeting_test_data()
        group = Group.objects.get(acronym='mars')
        session = Session.objects.filter(meeting=meeting,group=group).first()
        
        # test create
        filename = 'ietf42-testroom-20000101-0800.mp3'
        docs_before = Document.objects.filter(type='recording').count()
        doc = get_or_create_recording_document(filename,session)
        docs_after = Document.objects.filter(type='recording').count()
        self.assertEqual(docs_after,docs_before + 1)
        self.assertTrue(doc.external_url.endswith(filename))

        # test get
        docs_before = docs_after
        doc2 = get_or_create_recording_document(filename,session)
        docs_after = Document.objects.filter(type='recording').count()
        self.assertEqual(docs_after,docs_before)
        self.assertEqual(doc,doc2)

    def test_create_recording(self):
        meeting = make_meeting_test_data()
        group = Group.objects.get(acronym='mars')
        session = Session.objects.filter(meeting=meeting,group=group).first()
        filename = 'ietf42-testroomt-20000101-0800.mp3'
        url = settings.IETF_AUDIO_URL + 'ietf{}/{}'.format(meeting.number, filename)
        doc = create_recording(session, url)
        self.assertEqual(doc.name,'recording-42-mars-1')
        self.assertEqual(doc.group,group)
        self.assertEqual(doc.external_url,url)
        self.assertTrue(doc in session.materials.all())

    def test_get_next_sequence(self):
        meeting = make_meeting_test_data()
        group = Group.objects.get(acronym='mars')
        sequence = get_next_sequence(group,meeting,'recording')
        self.assertEqual(sequence,1)

    def test_send_audio_import_warning(self):
        length_before = len(outbox)
        send_audio_import_warning(['recording-43-badroom-20000101-0800.mp3'])
        self.assertEqual(len(outbox), length_before + 1)
        self.assertTrue('Audio file import' in outbox[-1]['Subject'])

class OldProceedingsTestCase(TestCase):
    ''' Ensure coverage of fragments of old proceedings generation until those are removed ''' 
    def setUp(self):
        self.session = SessionFactory(meeting__type_id='ietf')
        self.proceedings_dir = os.path.abspath("tmp-proceedings-dir")

        # This unintuitive bit is a consequence of the surprising implementation of meeting.get_materials_path
        self.saved_agenda_path = settings.AGENDA_PATH
        settings.AGENDA_PATH= self.proceedings_dir

        target_path = self.session.meeting.get_materials_path()
        if not os.path.exists(target_path):
            os.makedirs(target_path)

    def tearDown(self):
        shutil.rmtree(self.proceedings_dir)
        settings.AGENDA_PATH = self.saved_agenda_path

    def test_old_generate(self):
        create_proceedings(self.session.meeting,self.session.group,is_final=True)
