import sys
from django.test import TestCase
from django.test.client import Client
from ietf.meeting.models  import TimeSlot, Session, Schedule, ScheduledSession
from ietf.meeting.models  import Constraint
from ietf.group.models    import Group
from ietf.name.models     import ConstraintName
from settings import BADNESS_CONFLICT_1,BADNESS_CONFLICT_2,BADNESS_CONFLICT_3,BADNESS_UNPLACED,BADNESS_TOOSMALL_50,BADNESS_TOOSMALL_100,BADNESS_TOOBIG,BADNESS_MUCHTOOBIG

class ModelTestCase(TestCase):
    fixtures = [ 'names.xml',  # ietf/names/fixtures/names.xml for MeetingTypeName, and TimeSlotTypeName
                 'meeting83.json',
                 'constraint83.json',
                 'workinggroups.json',
                 'empty83.json',  # a partially placed schedule
                 'person.json',
                 'users.json' ]

    def test_ScheduleAllSessions(self):
        """
        return the list of all sessions that want to meet
        """
        mtg83 = Meeting.objects.get(number=83)
        wanttomeet = mtg83.sessions_that_can_meet
        self.assertEqual(len(wanttomeet), 144)

    def test_ScheduleAllSessions(self):
        """
        return the list of scheduled sessions, and sessions that have not been scheduled.
        """
        schedule = Schedule.objects.get(pk=103)
        assignments = schedule.group_mapping
        assigned = 0
        unassigned = 0
        for g,r in assignments.items():
            if len(r)>0:
                assigned += len(r)
            else:
                unassigned += 1
        self.assertEqual(assigned,   22)
        self.assertEqual(unassigned, 113)
        self.assertEqual(len(schedule.meeting.session_set.all()), 150)

    def test_calculatePlacedSession1(self):
        """
        calculate the fitness for a session that has been placed.
        """
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        assignments = schedule.group_mapping
        saag = mtg.session_set.get(group__acronym = 'saag')
        self.assertNotEqual(saag, None)
        self.assertNotEqual(assignments[saag.group], [])
        badness = saag.badness(assignments)
        self.assertEqual(badness, BADNESS_TOOBIG)

    def test_calculatePlacedSession2(self):
        """
        calculate the fitness for a session that has been placed.
        """

        # do some setup of these slots
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        ipsecme = mtg.session_set.get(group__acronym = 'ipsecme')
        websec  = mtg.session_set.get(group__acronym = 'websec')
        slot1   = schedule.scheduledsession_set.get(timeslot__id = 2373) # 2012-03-26 13:00 location_id=212 (242AB)
        slot2   = schedule.scheduledsession_set.get(timeslot__id = 2376) # 2012-03-26 13:00 location_id=213 (Maillot)
        slot1.session = ipsecme
        slot1.save()
        slot2.session = websec
        slot2.save()

        # now calculate badness
        assignments = schedule.group_mapping
        self.assertNotEqual(ipsecme, None)
        self.assertTrue(len(assignments[ipsecme.group]) > 0)
        badness = ipsecme.badness(assignments)
        self.assertEqual(badness, BADNESS_CONFLICT_3+BADNESS_TOOBIG)

    def test_calculateBadnessMtg83(self):
        """
        calculate the fitness for a session that has been placed.
        """

        # do some setup of these slots
        schedule = Schedule.objects.get(pk=24)
        self.assertEqual(schedule.calc_badness(), 3481200)

    def test_calculateUnPlacedSession(self):
        """
        calculate the fitness for a session that has not been placed
        """
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        assignments = schedule.group_mapping
        pkix = mtg.session_set.get(group__acronym = 'pkix')
        self.assertNotEqual(pkix, None)
        self.assertTrue(len(assignments[pkix.group]) == 0)
        badness = pkix.badness(assignments)
        self.assertEqual(badness, BADNESS_UNPLACED)

    def test_orderingOfConstaints(self):
        """
        test if Constraints order properly
        """
        schedule = Schedule.objects.get(pk=103)
        mtg = schedule.meeting
        group1   = Group.objects.get(acronym='pkix')
        group2   = Group.objects.get(acronym='ipsecme')
        conflict = ConstraintName.objects.get(slug="conflict", )
        conflic2 = ConstraintName.objects.get(slug="conflic2")
        conflic3 = ConstraintName.objects.get(slug="conflic3")
        c1 = Constraint.objects.create(name=conflict, meeting=mtg, source=group1, target=group2)
        c2 = Constraint.objects.create(name=conflic2, meeting=mtg, source=group1, target=group2)
        c3 = Constraint.objects.create(name=conflic3, meeting=mtg, source=group1, target=group2)
        self.assertTrue(c1 < c2)
        self.assertTrue(c2 < c3)
        self.assertTrue(c1 < c3)

