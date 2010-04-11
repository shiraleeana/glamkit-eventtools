import datetime
import os
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import get_model
from django.db.models.fields.related import ReverseSingleRelatedObjectDescriptor
from django.conf import settings
from django.db.models.loading import load_app
from django.core.management import call_command
from eventtools.tests.eventtools_testapp.models import *
from datetime import date, datetime, time
class TestModelMetaClass(TestCase):
    __module__ = __name__

    def setUp(self):
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS += ['eventtools.tests.eventtools_testapp']
        load_app('eventtools.tests.eventtools_testapp')
        call_command('flush', verbosity=0, interactive=False)
        call_command('syncdb', verbosity=0, interactive=False)
        self.Occ1 = get_model('eventtools_testapp', 'lectureeventoccurrence')
        self.Occ2 = get_model('eventtools_testapp', 'broadcasteventoccurrence')
        self.Occ3 = get_model('eventtools_testapp', 'lessoneventoccurrence')
        self.occs = [self.Occ1,
         self.Occ2,
         self.Occ3]
        self.Gen1 = get_model('eventtools_testapp', 'lectureeventoccurrencegenerator')
        self.Gen2 = get_model('eventtools_testapp', 'broadcasteventoccurrencegenerator')
        self.Gen3 = get_model('eventtools_testapp', 'lessoneventoccurrencegenerator')
        self.gens = [self.Gen1,
         self.Gen2,
         self.Gen3]



    def tearDown(self):
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS



    def test_model_metaclass_generation(self):
        '\n        Test that when we create a subclass of EventBase, a corresponding subclass of OccurrenceBase is generated automatically.        \n        '
        for (occ, gen,) in zip(self.occs, self.gens):
            if (occ == ):
                import pdb
                pdb.set_trace()
            self.assertTrue((occ != ))
            self.assertTrue((gen != ))
            self.assertTrue(isinstance(occ.generator, ReverseSingleRelatedObjectDescriptor))
            self.assertTrue(isinstance(gen.event, ReverseSingleRelatedObjectDescriptor))
            self.assertEqual(gen._occurrence_model_name, occ.__name__.lower())




    def test_event_without_variation(self):
        subject = 'Django testing for n00bs'
        lesson = LessonEvent.objects.create(subject=subject)
        gen = lesson.generators.create(first_start_date=date(2010, 1, 1), first_start_time=time(13, 0), first_end_date=, first_end_time=time(14, 0))
        occ = lesson.get_one_occurrence()
        self.assertEqual(occ.varied_event, )
        self.assertRaises(AttributeError, getattr, occ.varied_event, 'subject')
        self.assertRaises(AttributeError, setattr, occ, 'varied_event', 'foo')
        self.assertEqual(occ.unvaried_event.subject, subject)
        self.assertEqual(occ.merged_event.subject, subject)



    def test_event_occurrence_attributes(self):
        '\n        Test that event occurrences can override (any) field of their parent event\n        '
        te1 = LectureEvent.objects.create(location='The lecture hall', title='Lecture series on Butterflies')
        self.assertTrue(te1.wheelchair_access)
        gen = te1.generators.create(first_start_date=date(2010, 1, 1), first_start_time=time(13, 0), first_end_date=, first_end_time=time(14, 0))
        self.assertTrue(gen)
        occ = te1.get_one_occurrence()
        self.assertTrue(occ)
        self.assertEqual(occ, models.get_model('eventtools_testapp', 'lectureeventoccurrence')(generator=gen, varied_start_date=date(2010, 1, 1), varied_start_time=time(13, 0), varied_end_date=, varied_end_time=time(14, 0), unvaried_start_date=date(2010, 1, 1), unvaried_start_time=time(13, 0), unvaried_end_date=, unvaried_end_time=time(14, 0)))
        self.assertTrue(occ.unvaried_event.wheelchair_access)
        self.assertTrue(occ.merged_event.wheelchair_access)
        self.assertTrue(isinstance(occ.unvaried_event, LectureEvent))
        self.assertEqual(occ.merged_event.location, 'The lecture hall')
        self.assertEqual(occ.varied_event, )
        self.assertRaises(AttributeError, getattr, occ.varied_event, 'location')
        occ.varied_event = LectureEventVariation.objects.create(location='The foyer')
        self.assertEqual(occ.merged_event.location, 'The foyer')
        self.assertTrue((occ.varied_event.wheelchair_access == ))
        self.assertEqual(occ.merged_event.title, 'Lecture series on Butterflies')
        self.assertEqual(occ.varied_event.location, 'The foyer')
        self.assertEqual(occ.unvaried_event.location, 'The lecture hall')
        self.assertRaises(Exception, setattr, occ.merged_event.location, "shouldn't be writeable")
        occ.varied_event.location = 'The meeting room'
        occ.varied_event.wheelchair_access = False
        occ.varied_event.save()
        occ.save()
        self.assertTrue((occ.merged_event.location == 'The meeting room'))
        self.assertTrue((occ.varied_event.location == 'The meeting room'))
        self.assertTrue((occ.unvaried_event.location == 'The lecture hall'))
        self.assertEqual(occ.varied_event.wheelchair_access, False)
        self.assertEqual(occ.unvaried_event.wheelchair_access, True)
        self.assertEqual(occ.merged_event.wheelchair_access, False)
        te1.title = 'Lecture series on Lepidoptera'
        te1.save()
        occ = te1.get_one_occurrence()
        self.assertEqual(occ.unvaried_event.title, 'Lecture series on Lepidoptera')
        self.assertEqual(occ.merged_event.title, 'Lecture series on Lepidoptera')
        self.assertEqual(occ.varied_event.title, )



    def test_saving(self):
        te1 = LectureEvent.objects.create(location='The lecture hall', title='Lecture series on Butterflies')
        te1.generators.create(first_start_date=date(2010, 1, 1), first_start_time=time(13, 0), first_end_date=, first_end_time=time(14, 0))
        occ = te1.get_one_occurrence()
        num_variations1 = int(LectureEventVariation.objects.count())
        occ.save()
        num_variations2 = int(LectureEventVariation.objects.count())
        self.assertEqual(num_variations1, num_variations2)




#+++ okay decompyling
# decompiled 1 files: 1 okay, 0 failed, 0 verify failed
