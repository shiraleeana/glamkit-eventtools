import datetime
import os

from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import get_model

from eventtools.tests.events.models import *
# from eventtools.periods import Period, Month, Day
# from eventtools.utils import EventListManager
from datetime import date, datetime, time

# from testapp.models import *


class TestModelMetaClass(TestCase):
    def setUp(self):
        self.Occ1 = get_model("events", "lectureeventoccurrence")
        self.Occ2 = get_model("events", "broadcasteventoccurrence")
        self.Occ3 = get_model("events", "lessonoccurrence")
        
        self.occs = [self.Occ1, self.Occ2, self.Occ3,]

        self.Gen1 = get_model("events", "lectureeventoccurrencegenerator")
        self.Gen2 = get_model("events", "broadcasteventoccurrencegenerator")
        self.Gen3 = get_model("events", "lessonoccurrencegenerator")

        self.gens = [self.Gen1, self.Gen2, self.Gen3,]
    

    def test_model_metaclass_generation(self):
        """
        Test that when we create a subclass of EventBase, a corresponding subclass of OccurrenceBase is generated automatically.        
        """
        
        #Test that the occurrence models are automagically generated
        
        for occ, gen in zip(self.occs, self.gens):
            self.assertTrue(occ != None)
            self.assertTrue(gen != None)
            # do the relations between classes exist?
            self.assertTrue(isinstance(occ.generator, models.ForeignKey))
            self.assertTrue(isinstance(gen.event, models.ForeignKey))
            self.assertTrue(isinstance(occ.variation, models.ForeignKey))
    

        
    def test_event_occurrence_attributes(self):
        """
        Test that event occurrences can override (any) field of their parent event
        """
        te1 = LectureEvent.objects.create(location="The lecture hall", title="Lecture series on Butterflies")
        
        # one-shot generator
        te1.generators.create(first_start_date = date(2010, 1, 1), first_start_time = time(13,00), first_end_date = None, first_end_time = time(14,00)) #no rules = this is when it's on

        occ = te1.get_one_occurrence()

        self.assertTrue(isinstance(occ.unvaried_event, LectureEvent))
        self.assertEqual(occ.location, "The lecture hall")
        self.assertTrue(occ.varied_event, None) #you have to explicitly create a variation.
        self.assertRaises(AttributeError, occ.varied_event.location)
        
        #Now make a variation
        
        occ.varied_event = LectureEventVariation.objects.create(location='The foyer')
        
        self.assertEqual(occ.location, "The foyer")
        self.assertEqual(occ.title, "Lecture series of Butterflies")
        self.assertEqual(occ.varied_event.location, "The foyer")
        self.assertEqual(occ.unvaried_event.location, "The lecture hall")
        self.assertRaises(Exception, occ.setattr, "location", "shouldn't be writeable")
        
        # now modify the variation
        occ.varied_event.location="The meeting room" #the location is an override here.
        
        #test that if we update the original event, then eventoccurences continue to only override the things they have specifically defined.
        te1.title = "Lecture series on Lepidoptera"
        te1.save()

        self.assertTrue(occ.location=="The meeting room")
        self.assertTrue(occ.varied_event.location=="The meeting room")
        self.assertTrue(occ.unvaried_event.location=="The lecture hall")
        self.assertTrue(occ.title=="Lecture series on Lepidoptera")
        self.assertTrue(occ.unvaried_event.title=="Lecture series on Lepidoptera")
        self.assertEqual(occ.varied_event.title, None)
        
        
        
        
    def test_saving(self):
    
        te1 = LectureEvent.objects.create(location="The lecture hall", title="Lecture series on Butterflies")
        
        # one-shot generator
        te1.generators.create(first_start_date = date(2010, 1, 1), first_start_time = time(13,00), first_end_date = None, first_end_time = time(14,00)) #no rules = this is when it's on
        occ = te1.get_one_occurrence()
    
        # test that saving an occurrence without a variation doesn't save an empty variation
        num_variations1 = int(LectureEventVariation.objects.count())
        assertTrue(isinstance(occ.varied_event, LectureEventVariation))
        occ.save()
        num_variations2 = int(LectureEventVariation.objects.count())
        assertEqual(num_variation1, num_variations2)
        
        
               
        
        
        
# class TestEvent(TestCase):
#     def setUp(self):
#         rule = Rule(frequency = "WEEKLY")
#         rule.save()
#         generator = OccurrenceGenerator(start = datetime(2010, 1, 1, 13), end = time(14))
#     def setUp(self):
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
