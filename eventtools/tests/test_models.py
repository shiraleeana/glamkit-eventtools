import datetime
import os

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import get_model

from eventtools.tests.events.models import TestEvent1, TestEvent2
from eventtools.periods import Period, Month, Day
from eventtools.utils import EventListManager

# from testapp.models import *


class TestModelMetaClass(TestCase):
#    def setUp(self):
        
        
    def test_model_metaclass_generation(self):
        """
        Test that when we create a subclass of EventBase, a corresponding subclass of OccurrenceBase is generated automatically.        
        """
        
        #Assert that the models are automagically generated
        E1O = get_model("app_name", "TestEvent1Occurrence")
        E2O = get_model("app_name", "TestEvent2Occurrence")
        
        
        self.assertTrue(E1O != None)
        self.assertTrue(E2O != None)
        
        #Do the TestEventOccurrence models contain all the fields from the Event model?
        
        for event_model_pair in [(TestEvent1, E1O), (TestEvent2, E20)]:        
            for attr_name in dir(event_model_pair[0]):
                attr = getattr(event_model_pair[0], attr_name)
                # if the attribute is a ModelField, then check the corresponding -Occurrence model has the equivalent field.
                if isinstance(attr, ModelField):
                    self.assertTrue(has_attr(event_model_pair[1], attr))
                    
        #sanity check: make sure TestEvent2Occurrence doesn't end up with a location field through metaclass weirdness
        self.assertEqual(hasattr(TestEvent2Occurrence, "location"), False)
        
    def test_event_occurrence_attributes(self):
        """
        Test that event occurrences can override (any) field of their parent event
        """
        te1 = TestEvent1.objects.create(location="The lecture hall", title="Lecture series on Butterflies")

        #standard django submodel stuff
        self.assertTrue(hasattr(te1, "title"))
        
        oe = TestEvent1Occurrence.object.create(event=te1, location="The foyer") #the location is an override here.
        
        self.assertTrue(oe.location=="The foyer")
        self.assertTrue(oe.title=="Lecture series of Butterflies")
        
        #test that if we update the original event, then eventoccurences continue to only override the things they have specifically defined.
        te1.title = "Lecture series on Lepidoptera"
        te1.save()

        self.assertTrue(oe.location=="The foyer")
        self.assertTrue(oe.title=="Lecture series on Lepidoptera")
        
        

        

# class TestEvent(TestCase):
#     def setUp(self):
#         rule = Rule(frequency = "WEEKLY")
#         rule.save()
#         cal = Calendar(name="MyCal")
#         cal.save()
#         self.recurring_data = {
#                 'title': 'Recent Event',
#                 'start': datetime.datetime(2008, 1, 5, 8, 0),
#                 'end': datetime.datetime(2008, 1, 5, 9, 0),
#                 'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
#                 'rule': rule,
#                 'calendar': cal
#                }
#         self.data = {
#                 'title': 'Recent Event',
#                 'start': datetime.datetime(2008, 1, 5, 8, 0),
#                 'end': datetime.datetime(2008, 1, 5, 9, 0),
#                 'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
#                 'calendar': cal
#                }
# 
# 
#     def test_recurring_event_get_occurrences(self):
#         recurring_event = Event(**self.recurring_data)
#         occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 12, 0, 0),
#                                     end=datetime.datetime(2008, 1, 20, 0, 0))
#         self.assertEquals(["%s to %s" %(o.start, o.end) for o in occurrences],
#             ['2008-01-12 08:00:00 to 2008-01-12 09:00:00', '2008-01-19 08:00:00 to 2008-01-19 09:00:00'])
# 
#     def test_event_get_occurrences_after(self):
#         recurring_event=Event(**self.recurring_data)
#         recurring_event.save()
#         occurrences = recurring_event.get_occurrences(start=datetime.datetime(2008, 1, 5),
#             end = datetime.datetime(2008, 1, 6))
#         occurrence = occurrences[0]
#         occurrence2 = recurring_event.occurrences_after(datetime.datetime(2008,1,5)).next()
#         self.assertEqual(occurrence, occurrence2)
# 
#     def test_get_occurrence(self):
#         event = Event(**self.recurring_data)
#         event.save()
#         occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0))
#         self.assertEqual(occurrence.start, datetime.datetime(2008,1,5,8))
#         occurrence.save()
#         occurrence = event.get_occurrence(datetime.datetime(2008, 1, 5, 8, 0))
#         self.assertTrue(occurrence.pk is not None)
# 
# 
# class TestOccurrence(TestCase):
#     def setUp(self):
#         rule = Rule(frequency = "WEEKLY")
#         rule.save()
#         cal = Calendar(name="MyCal")
#         cal.save()
#         self.recurring_data = {
#                 'title': 'Recent Event',
#                 'start': datetime.datetime(2008, 1, 5, 8, 0),
#                 'end': datetime.datetime(2008, 1, 5, 9, 0),
#                 'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
#                 'rule': rule,
#                 'calendar': cal
#                }
#         self.data = {
#                 'title': 'Recent Event',
#                 'start': datetime.datetime(2008, 1, 5, 8, 0),
#                 'end': datetime.datetime(2008, 1, 5, 9, 0),
#                 'end_recurring_period' : datetime.datetime(2008, 5, 5, 0, 0),
#                 'calendar': cal
#                }
#         self.recurring_event = Event(**self.recurring_data)
#         self.recurring_event.save()
#         self.start = datetime.datetime(2008, 1, 12, 0, 0)
#         self.end = datetime.datetime(2008, 1, 27, 0, 0)
# 
#     def test_presisted_occurrences(self):
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         persisted_occurrence = occurrences[0]
#         persisted_occurrence.save()
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         self.assertTrue(occurrences[0].pk)
#         self.assertFalse(occurrences[1].pk)
# 
#     def test_moved_occurrences(self):
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         moved_occurrence = occurrences[1]
#         span_pre = (moved_occurrence.start, moved_occurrence.end)
#         span_post = [x + datetime.timedelta(hours=2) for x in span_pre]
#         # check has_occurrence on both periods
#         period_pre = Period([self.recurring_event], span_pre[0], span_pre[1])
#         period_post = Period([self.recurring_event], span_post[0], span_post[1])
#         self.assertTrue(period_pre.has_occurrences())
#         self.assertFalse(period_post.has_occurrences())
#         # move occurrence
#         moved_occurrence.move(moved_occurrence.start+datetime.timedelta(hours=2),
#                               moved_occurrence.end+datetime.timedelta(hours=2))
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         self.assertTrue(occurrences[1].moved)
#         # check has_occurrence on both periods (the result should be reversed)
#         period_pre = Period([self.recurring_event], span_pre[0], span_pre[1])
#         period_post = Period([self.recurring_event], span_post[0], span_post[1])
#         self.assertFalse(period_pre.has_occurrences())
#         self.assertTrue(period_post.has_occurrences())
# 
#     def test_cancelled_occurrences(self):
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         cancelled_occurrence = occurrences[2]
#         cancelled_occurrence.cancel()
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         self.assertTrue(occurrences[2].cancelled)
#         cancelled_occurrence.uncancel()
#         occurrences = self.recurring_event.get_occurrences(start=self.start,
#                                     end=self.end)
#         self.assertFalse(occurrences[2].cancelled)
# 
