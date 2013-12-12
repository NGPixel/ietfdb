from __future__ import absolute_import
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException
import django.test
from ietf.utils import TestCase
from ietf.utils.test_utils import RealDatabaseTest

from ietf.meeting.helpers import get_meeting, get_schedule
import datetime

class SeleniumTestCase(django.test.TestCase,RealDatabaseTest):
    def setUp(self):
        self.setUpRealDatabase()
        self.driver = webdriver.Firefox()
        fp = webdriver.FirefoxProfile()
        fp.set_preference("webdriver.firefox.profile", "selenium")
        fp.update_preferences()
        self.driver.implicitly_wait(30)
        self.base_url = "http://localhost:8000"
        self.verificationErrors = []
        self.accept_next_alert = True

    def test_seltest1_python(self):
        driver = self.driver
        driver.maximize_window()

        m83 = get_meeting(83)
        a83 = m83.agenda
        forces_request = m83.session_set.get(group__acronym = "forces")
        ipsec_request  = m83.session_set.get(group__acronym = "ipsecme")

        driver.get(self.base_url + "/meeting/83/schedule/%s/edit" % a83.name)

        print "The test web server has to run with user wnl who owns mtg83"
        print "Starting test"
        itercount=0
        while itercount < 1000 and not self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"):
            time.sleep(2)
            itercount = itercount+1
        self.assertTrue(self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"))
        print "Found page loading"

        itercount=0
        while itercount < 1000 and self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"):
            time.sleep(2)
            itercount = itercount+1
        self.assertFalse(self.is_element_visible(how=By.CSS_SELECTOR,what="#spinner"))
        print "Found page loaded"

        print "clicking ipsecme"
        driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (ipsec_request.pk)).click()
        action_chain1 = ActionChains(driver)
        action_chain2 = ActionChains(driver)

        # find current forces timeslot in database
        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "253", "initial conditions wrong")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,26,15,10), "initial time wrong")

        print "clicking forces"
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        forces.click()

        monday_room_253_ts = m83.timeslot_set.get(location__name = "253",
                                                  time = datetime.datetime(2012,3,26,15,10))
        friday_room_252A_ts = m83.timeslot_set.get(location__name = "252A",
                                                  time = datetime.datetime(2012,3,30,12,30))

        monday_room_253  = driver.find_element_by_css_selector("#" + forces_ts.js_identifier)
        friday_room_252A = driver.find_element_by_css_selector("#" + friday_room_252A_ts.js_identifier)
        print "moving to Friday slot: %s" % (friday_room_252A_ts.js_identifier)
        time.sleep(6)
        action_chain1.drag_and_drop(forces, friday_room_252A).perform()

        # not sure how else to know it is done yet.
        print "waiting for database operation to complete"
        time.sleep(15)

        forces_ss = a83.scheduledsession_set.get(session = forces_request)
        forces_ts = forces_ss.timeslot
        self.assertEqual(forces_ts.location.name, "252A")
        self.assertEqual(forces_ts.time, datetime.datetime(2012,3,30,12,30))

        print "moving it back to Monday"
        # Have to find it again since we moved it
        forces = driver.find_element_by_css_selector("#session_%u > tbody > #meeting_event_title > th.meeting_obj" % (forces_request.pk))
        action_chain2.drag_and_drop(forces, monday_room_253).perform()
        time.sleep(15)

    def is_element_present(self, how, what):
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return True

    def is_element_visible(self, how, what):
        try:
           element = self.driver.find_element(by=how, value=what)
        except NoSuchElementException, e:
            return False
        return element.is_displayed()

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException, e:
            return False
        return True

    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally:
            self.accept_next_alert = True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)
        self.tearDownRealDatabase()

if __name__ == "__main__":
    unittest.main()

