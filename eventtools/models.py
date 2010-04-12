from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.defaultfilters import date as date_filter
from datetime import date, datetime, time
from django.core.exceptions import ObjectDoesNotExist
from eventtools.utils import OccurrenceReplacer
from dateutil import rrule
import sys

from django.db.models.base import ModelBase

class OccurrenceGeneratorModelBase(ModelBase):
    """
    When we create an OccurrenceGenerator, add to it an occurrence_model_name so it knows what to generate.
    """
    
    def __init__(cls, name, bases, attrs):
        if name != 'OccurrenceGeneratorBase': # This should only fire if this is a subclass
            model_name = name[0:-len("Generator")].lower()
            cls.add_to_class('_occurrence_model_name', model_name)
        super(OccurrenceGeneratorModelBase, cls).__init__(name, bases, attrs)
    
class OccurrenceGeneratorBase(models.Model):
    """
    Defines a set of repetition rules for an event
    """
    
    __metaclass__ = OccurrenceGeneratorModelBase
    
    first_start_date = models.DateField()
    first_start_time = models.TimeField()
    first_end_date = models.DateField(null = True, blank = True)
    first_end_time = models.TimeField() #wasn't originally required, but it turns out you do have to say when an event ends...
    rule = models.ForeignKey('Rule', verbose_name="How often does it repeat?", null = True, blank = True, help_text="Select '----' for a one-off event.")
    repeat_until = models.DateTimeField(null = True, blank = True, help_text="This date is ignored for one-off events.")
    
    class Meta:
        ordering = ('first_start_date', 'first_start_time')
        abstract = True
        verbose_name = 'occurrence generator'
        verbose_name_plural = 'occurrence generators'
    
    def _occurrence_model(self):
        return models.get_model(self._meta.app_label, self._occurrence_model_name)
    occurrence_model = property(_occurrence_model)

        
    def _end_recurring_period(self):
        return self.end
#         if self.end:
#             return datetime.datetime.combine(self.end_day, datetime.time.max)
#         else:
#             return None	
    end_recurring_period = property(_end_recurring_period)

    # for backwards compatibility    
    def _get_start(self):
        return datetime.combine(self.first_start_date, self.first_start_time)

    def _set_start(self, value):
        self.first_start_date = value.date()
        self.first_start_time = value.time()
        
    start = property(_get_start, _set_start)
    
    def _get_end_time(self):
        return self.first_end_time
        
    def _set_end_time(self, value):
        self.first_end_time = value
    
    end_time = property(_get_end_time, _set_end_time)    
        
    def _end(self):
        return datetime.combine(self.first_end_date or self.first_start_date, self.first_end_time)
    end = property(_end)

    def __unicode__(self):
        date_format = u'l, %s' % ugettext("DATE_FORMAT")
        return ugettext('%(title)s: %(start)s-%(end)s') % {
            'title': unicode(self.event),
            'start': date_filter(self.start, date_format),
            'end': date_filter(self.end, date_format),
        }

    def get_occurrences(self, start, end):
#         """
#         >>> rule = Rule(frequency = "MONTHLY", name = "Monthly")
#         >>> rule.save()
#         >>> event = Event(rule=rule, start=datetime.datetime(2008,1,1), end=datetime.datetime(2008,1,2))
#         >>> event.rule
#         <Rule: Monthly>
#         >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
#         >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
#         ['2008-02-01 00:00:00 to 2008-02-02 00:00:00', '2008-03-01 00:00:00 to 2008-03-02 00:00:00']
# 
#         Ensure that if an event has no rule, that it appears only once.
# 
#         >>> event = Event(start=datetime.datetime(2008,1,1,8,0), end=datetime.datetime(2008,1,1,9,0))
#         >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
#         >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
#         []
# 
#         """
        exceptional_occurrences = self.occurrences.all()
        occ_replacer = OccurrenceReplacer(exceptional_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their exceptional counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
              final_occurrences.append(occ)
        # then add exceptional occurrences which originated outside of this period but now
        # fall within it
        final_occurrences += occ_replacer.get_additional_occurrences(start, end)
        return final_occurrences
        

    def get_rrule_object(self):
        if self.rule is not None:
            if self.rule.complex_rule:
                try:
                    return rrule.rrulestr(str(self.rule.complex_rule),dtstart=self.start)
                except:
                    pass
            params = self.rule.get_params()
            frequency = 'rrule.%s' % self.rule.frequency
            simple_rule = rrule.rrule(eval(frequency), dtstart=self.start, **params)
            set = rrule.rruleset()
            set.rrule(simple_rule)
#             goodfriday = rrule.rrule(rrule.YEARLY, dtstart=self.start, byeaster=-2)
#             christmas = rrule.rrule(rrule.YEARLY, dtstart=self.start, bymonth=12, bymonthday=25)
#             set.exrule(goodfriday)
#             set.exrule(christmas)
            return set

    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        occ = self.occurrence_model(
            generator=self,
            varied_start_date=start.date(),
            varied_start_time=start.time(),
            varied_end_date=end.date(),
            varied_end_time=end.time(),
            unvaried_start_date=start.date(),
            unvaried_start_time=start.time(),
            unvaried_end_date=end.date(),
            unvaried_end_time=end.time(),
        )
        return occ
    
    def get_one_occurrence(self):
        try:
            occ = self.occurrence_model.objects.filter(generator__event=self)[0]
        except IndexError:
            occ = self.occurrence_model(
                generator=self,
                varied_start_date=self.first_start_date,
                varied_start_time=self.first_start_time,
                varied_end_date=self.first_end_date,
                varied_end_time=self.first_start_time,
                unvaried_start_date=self.first_start_date,
                unvaried_start_time=self.first_start_time,
                unvaried_end_date=self.first_end_date,
                unvaried_end_time=self.first_start_time
            )
        return occ

    def get_occurrence(self, date):
        rule = self.get_rrule_object()
        if rule:
            next_occurrence = rule.after(date, inc=True)
        else:
            next_occurrence = self.start
        if next_occurrence == date:
            try:
                return self.occurrence_model.objects.get(generator__event = self, unvaried_start_date = date)
            except self.occurrence_model.DoesNotExist:
                return self._create_occurrence(next_occurrence)


    def _get_occurrence_list(self, start, end):
        """
        returns a list of occurrences for this event from start to end.
        """
        difference = (self.end - self.start)
        if self.rule is not None:
            occurrences = []
            if self.end_recurring_period and self.end_recurring_period < end:
                end = self.end_recurring_period
            rule = self.get_rrule_object()
            o_starts = rule.between(start-difference, end, inc=True)
            for o_start in o_starts:
                o_end = o_start + difference
                occurrences.append(self._create_occurrence(o_start, o_end))
            return occurrences
        else:
            # check if event is in the period
            if self.start < end and self.end >= start:
                return [self._create_occurrence(self.start)]
            else:
                return []

    def _occurrences_after_generator(self, after=None):
        """
        returns a generator that produces unexceptional occurrences after the
        datetime ``after``.
        """

        if after is None:
            after = datetime.datetime.now()
        rule = self.get_rrule_object()
        if rule is None:
            if self.end > after:
                yield self._create_occurrence(self.start, self.end)
            raise StopIteration
        date_iter = iter(rule)
        difference = self.end - self.start
        while True:
            o_start = date_iter.next()
            if o_start > self.end_recurring_period:
                raise StopIteration
            o_end = o_start + difference
            if o_end > after:
                yield self._create_occurrence(o_start, o_end)


    def occurrences_after(self, after=None):
        """
        returns a generator that produces occurrences after the datetime
        ``after``.	Includes all of the exceptional Occurrences.
        """
        occ_replacer = OccurrenceReplacer(self.occurrence_set.all())
        generator = self._occurrences_after_generator(after)
        while True:
            next = generator.next()
            yield occ_replacer.get_occurrence(next)


class MergedObject():
    """
    Objects of this class behave as though they are a merge of two other objects (which we'll call General and Special). The attributes of Special override the corresponding attributes of General, *unless* the value of the attribute in Special == None.
    
    All attributes are read-only, to save you from a world of pain.
    
    """

    def __init__(self, general, special):
        self._general = general
        self._special = special
        
    def __getattr__(self, value):
        
        try:
            result = getattr(self._special, value)
            if result == None:
                raise AttributeError
        except AttributeError:
            result = getattr(self._general, value)

        return result
        
    def __setattr__(self, attr, value):
        if attr in ['_general', '_special']:
            self.__dict__[attr] = value
        else:
            raise AttributeError("Set the attribute on one of the objects that are being merged.")
    
        

class OccurrenceBase(models.Model):
    varied_start_date = models.DateField(blank=True, null=True, db_index=True)
    varied_start_time = models.TimeField(blank=True, null=True, db_index=True)
    varied_end_date = models.DateField(blank=True, null=True, db_index=True)
    varied_end_time = models.TimeField(blank=True, null=True, db_index=True)
    unvaried_start_date = models.DateField(db_index=True)
    unvaried_start_time = models.TimeField(db_index=True)
    unvaried_end_date = models.DateField(db_index=True, null=True)
    unvaried_end_time = models.TimeField(db_index=True, null=True)
    cancelled = models.BooleanField(_("cancelled"), default=False)
    
    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")
        abstract = True
        unique_together = ('unvaried_start_date', 'unvaried_start_time', 'unvaried_end_date', 'unvaried_end_time')


    def _merged_event(self): #bit slow, but friendly
        return MergedObject(self.unvaried_event, self.varied_event)
    merged_event = property(_merged_event)
        
    # for backwards compatibility    
    def _get_varied_start(self):
        return datetime.combine(self.varied_start_date, self.varied_start_time)

    def _set_varied_start(self, value):
        self.varied_start_date = value.date
        self.varied_start_time = value.time
        
    start = varied_start = property(_get_varied_start, _set_varied_start)
    
    def _get_varied_end(self):
        return datetime.combine(self.varied_end_date, self.varied_end_time)

    def _set_varied_end(self, value):
        self.varied_end_date = value.date
        self.varied_end_time = value.time
    
    end = varied_end = property(_get_varied_end, _set_varied_end)    
        
    def _get_unvaried_start(self):
        return datetime.combine(self.unvaried_start_date, self.unvaried_start_time)

    def _set_unvaried_start(self, value):
        self.unvaried_start_date = value.date()
        self.unvaried_start_time = value.time()
        
    original_start = unvaried_start = property(_get_unvaried_start, _set_unvaried_start)
    
    def _get_unvaried_end(self):
        return datetime.combine(self.unvaried_end_date, self.unvaried_end_time)

    def _set_unvaried_end(self, value):
        self.unvaried_end_date = value.date
        self.unvaried_end_time = value.time
    
    original_end = unvaried_end = property(_get_unvaried_end, _set_unvaried_end)    
        

# 
#     def moved(self):
#         return self.original_start != self.start or self.original_end != self.end
#     moved = property(moved)
# 
#     def move(self, new_start, new_end):
#         self.start = new_start
#         self.end = new_end
#         self.save()
# 
#     def cancel(self):
#         self.cancelled = True
#         self.save()
# 
#     def uncancel(self):
#         self.cancelled = False
#         self.save()


    def __unicode__(self):
        return ugettext("%(event)s: %(day)s") % {
            'event': self.generator.event.title,
            'day': self.varied_start.strftime('%a, %d %b %Y'),
        }

#     def __cmp__(self, other):
#         rank = cmp(self.start, other.start)
#         if rank == 0:
#             return cmp(self.end, other.end)
#         return rank
# 
#     def __eq__(self, other):
#         return self.event == other.event and self.original_start == other.original_start and self.original_end == other.original_end
        
    def _get_varied_event(self):
        try:
            return getattr(self, "_varied_event", None)
        except:
            return None
    def _set_varied_event(self, v):
        if "_varied_event" in dir(self): #for a very weird reason, hasattr(self, "_varied_event") fails. Perhaps this is because it is injected by __init__ in the metaclass, not __new__.
            self._varied_event = v
        else:
            raise AttributeError("You can't set an event variation for an event class with no 'varied_by' attribute.")
    varied_event = property(_get_varied_event, _set_varied_event)

    def _get_unvaried_event(self):
        return self.generator.event
    unvaried_event = property(_get_unvaried_event)



class EventModelBase(ModelBase):
    def __init__(cls, name, bases, attrs):
        """
        Dynamically build two related classes to handle occurrences.
        
        The two generated classes are ModelNameOccurrence and ModelNameOccurrenceGenerator.
        
        If the EventBase subclass is called e.g. LectureEvent, then the two generated class will be called LectureEventOccurrence and LectureEventOccurrenceGenerator (yeesh, but end-user never sees these.)
        
        """
        if name != 'EventBase': # This should only fire if this is a subclass (maybe we should make devs apply this metaclass to their subclass instead?)
            # Build names for the new classes
            occ_name = "%s%s" % (name, "Occurrence")
            gen_name = "%s%s" % (occ_name, "Generator")
        
            cls.add_to_class('_occurrence_model_name', occ_name)
            cls.add_to_class('_generator_model_name', gen_name)
        
            # Create the generator class
            # globals()[gen_name] # < injecting into globals doesn't work with some of django's import magic. We have to inject the new class directly into the module that contains the EventBase subclass. I am AMAZED that you can do this, and have it still work for future imports.
            setattr(sys.modules[cls.__module__], gen_name, type(gen_name,
                    (OccurrenceGeneratorBase,),
                    dict(__module__ = cls.__module__,),
                )
            )
            generator_class = sys.modules[cls.__module__].__dict__[gen_name]
            
            # add a foreign key back to the event class
            generator_class.add_to_class('event', models.ForeignKey(cls, related_name = 'generators'))

            # Create the occurrence class
            # globals()[occ_name]
            setattr(sys.modules[cls.__module__], occ_name, type(occ_name,
                    (OccurrenceBase,),
                    dict(__module__ = cls.__module__,),
                )
            )
            occurrence_class = sys.modules[cls.__module__].__dict__[occ_name]

            # import pdb; pdb.set_trace()
            

            occurrence_class.add_to_class('generator', models.ForeignKey(generator_class, related_name = 'occurrences'))
            if hasattr(cls, 'varied_by'):
                occurrence_class.add_to_class('_varied_event', models.ForeignKey(cls.varied_by, related_name = 'occurrences', null=True))

        super(EventModelBase, cls).__init__(name, bases, attrs)
        
class EventBase(models.Model):
    """
    Event information minus the scheduling details
    
    Event scheduling is handled by one or more OccurrenceGenerators
    """
    __metaclass__ = EventModelBase

    class Meta:
        abstract = True

    def _occurrence_model(self):
        return models.get_model(self._meta.app_label, self._occurrence_model_name)
    occurrence_model = property(_occurrence_model)

    def _generator_model(self):
        return models.get_model(self._meta.app_label, self._generator_model_name)
    generator_model = property(_generator_model)

    def primary_generator(self):
        return self.generators.order_by('first_start_date', 'first_start_time')[0]
        
    def get_one_occurrence(self):
        try:
            return self.generators.all()[0].get_one_occurrence()
        except IndexError:
            raise IndexError("This Event type has no generators defined")
    
    def get_first_occurrence(self): # should return an actual occurrence
        return self.primary_generator().start		
        
    def get_last_day(self):
        lastdays = []
        for generator in self.generators.all():
            if not generator.end_recurring_period:
                return False
            lastdays.append(generator.end_recurring_period)
        lastdays.sort()
        return lastdays[-1]

    def _has_zero_generators(self):
        return self.generators.count() == 0
    has_zero_generators = property(_has_zero_generators)
        
    def _has_multiple_occurrences(self):
        return self.generators.count() > 1 or (self.generators.count() > 0 and self.generators.all()[0].rule != None)
    has_multiple_occurrences = property(_has_multiple_occurrences)

    def edit_occurrences_link(self):
        """ An admin link """
        if self.has_multiple_occurrences:
            return '<a href="%s/occurrences/">%s</a>' % (self.id, unicode(_("add or edit occurrences")))
        if self.has_zero_generators:
            return _('(has no occurrence generators)')
        return _("(has only one occurrence)")
    edit_occurrences_link.allow_tags = True
    edit_occurrences_link.short_description = _("Occurrences")
    
    def get_absolute_url(self):
        return "/event/%s/" % self.id
    
    def next_occurrences(self):
        from events.periods import Period
        first = False
        last = False
        for gen in self.generators.all():
            if not first or gen.start < first:
                first = gen.start
            if gen.rule and not gen.end_day:
                last = False # at least one rule is infinite
                break
            if not gen.end_day:
                genend = gen.start
            else:
                genend = gen.end_recurring_period
            if not last or genend > last:
                last = genend
        if last:
            period = Period(self.generators.all(), first, last)
        else:
            period = Period(self.generators.all(), datetime.datetime.now(), datetime.datetime.now() + datetime.timedelta(days=28))		
        return period.get_occurrences()

freqs = (
    ("YEARLY", _("Yearly")),
    ("MONTHLY", _("Monthly")),
    ("WEEKLY", _("Weekly")),
    ("DAILY", _("Daily")),
    ("HOURLY", _("Hourly")),
)

class Rule(models.Model):
    """
    This defines a rule by which an event will repeat.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of repetition.
    * description - a short description describing this type of repetition.
    * frequency - the base repetition period
    * param - extra params required to define this type of repetition. The params
      should follow this format:

        param = [rruleparam:value;]*
        rruleparam = see list below
        value = int[,int]*

      The options are: (documentation for these can be found at
      http://labix.org/python-dateutil#head-470fa22b2db72000d7abe698a5783a46b0731b57)
        ** count
        ** bysetpos
        ** bymonth
        ** bymonthday
        ** byyearday
        ** byweekno
        ** byweekday
        ** byhour
        ** byminute
        ** bysecond
        ** byeaster
    """
    name = models.CharField(_("name"), max_length=100, help_text=_("a short friendly name for this repetition."))
    description = models.TextField(_("description"), blank=True, help_text=_("a longer description of this type of repetition."))
    common = models.BooleanField(help_text=_("common rules appear at the top of the list."))
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10, blank=True, help_text=_("the base repetition period."))
    params = models.TextField(_("inclusion parameters"), blank=True, help_text=_("extra params required to define this type of repetition."))
    complex_rule = models.TextField(_("complex rules"), help_text=_("over-rides all other settings."), blank=True)

    class Meta:
        verbose_name = _('repetition rule')
        verbose_name_plural = _('repetition rules')
        ordering = ('-common', 'name')

    def get_params(self):
        """
        >>> rule = Rule(params = "count:1;bysecond:1;byminute:1,2,4,5")
        >>> rule.get_params()
        {'count': 1, 'byminute': [1, 2, 4, 5], 'bysecond': 1}
        """
    	params = self.params
        if params is None:
            return {}
        params = params.split(';')
        param_dict = []
        for param in params:
            param = param.split(':')
            if len(param) == 2:
                param = (str(param[0]), [int(p) for p in param[1].split(',')])
                if len(param[1]) == 1:
                    param = (param[0], param[1][0])
                param_dict.append(param)
        return dict(param_dict)
        
    def __unicode__(self):
        """Human readable string for Rule"""
        return self.name

