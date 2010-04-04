from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from django.template.defaultfilters import date
import datetime

class EventBase(models.Model):
    """
    A class of event
    
    Event scheduling is handled by one or more OccurrenceGenerators
    """
    title = models.CharField(_("Title"), max_length = 255)
    short_title = models.CharField(_("Short title"), max_length = 255, blank=True)
    schedule_description = models.CharField(_("Plain English description of schedule"), max_length=255, blank=True)

    class Meta:
        abstract = True

    def primary_generator(self):
        return self.generators.order_by('start')[0]
    
    def get_first_occurrence(self):
        return self.primary_generator().start		
        
    def get_last_day(self):
        lastdays = []
        for generator in self.generators.all():
            if not generator.end_recurring_period:
                return False
            lastdays.append(generator.end_recurring_period)
        lastdays.sort()
        return lastdays[-1]

    def has_multiple_occurrences(self):
        if self.generators.count() > 1 or (self.generators.count() > 0 and self.generators.all()[0].rule != None):
            return '<a href="%s/occurrences/">edit / add occurrences</a>' % self.id
        else:
            return ""
    has_multiple_occurrences.allow_tags = True
    
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

freqs = (   ("YEARLY", _("Yearly")),
            ("MONTHLY", _("Monthly")),
            ("WEEKLY", _("Weekly")),
            ("DAILY", _("Daily")),
            ("HOURLY", _("Hourly")),
            ("MINUTELY", _("Minutely")),
            ("SECONDLY", _("Secondly")))

class Rule(models.Model):
    """
    This defines a rule by which an event will recur.  This is defined by the
    rrule in the dateutil documentation.

    * name - the human friendly name of this kind of recursion.
    * description - a short description describing this type of recursion.
    * frequency - the base recurrence period
    * param - extra params required to define this type of recursion. The params
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
    name = models.CharField(_("name"), max_length=100)
    description = models.TextField(_("description"), blank=True)
    common = models.BooleanField()
    frequency = models.CharField(_("frequency"), choices=freqs, max_length=10, blank=True)
    params = models.TextField(_("inclusion parameters"), blank=True)
    complex_rule = models.TextField(_("complex rules (over-rides all other settings)"), blank=True)

    class Meta:
        verbose_name = _('rule')
        verbose_name_plural = _('rules')
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

class OccurrenceGeneratorBase(models.Model):
    """
    Defines a set of repetition rules for an event
    
    TO DO: implement without requiring subclass
    """
    start = models.DateTimeField()
    endtime = models.TimeField(blank=True, null=True)
    rule = models.ForeignKey(Rule, verbose_name="Repetition rule", null = True, blank = True, help_text="Select '----' for a one time only event.")
    end_day = models.DateField("end recurring period", null = True, blank = True, help_text="This date is ignored for one time only events.")

    class Meta:
        ordering = ('start',)
        abstract = True
        verbose_name = 'occurrence generator'
        verbose_name_plural = 'occurrence generators'

    def _end_recurring_period(self):
        if self.end_day:
            return datetime.datetime.combine(self.end_day, datetime.time.max)
        else:
            return None	
    end_recurring_period = property(_end_recurring_period)
        
    def _end(self):
        if self.endtime:
            return datetime.datetime.combine(self.start.date(), self.endtime)
        else:
            return self.start
    end = property(_end)

    def __unicode__(self):
        date_format = u'l, %s' % ugettext("DATE_FORMAT")
        return ugettext('%(title)s: %(start)s-%(end)s') % {
            'title': self.event.title,
            'start': date(self.start, date_format),
            'end': date(self.end, date_format),
        }

    def get_occurrences(self, start, end):
        """
        >>> rule = Rule(frequency = "MONTHLY", name = "Monthly")
        >>> rule.save()
        >>> event = Event(rule=rule, start=datetime.datetime(2008,1,1), end=datetime.datetime(2008,1,2))
        >>> event.rule
        <Rule: Monthly>
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        ['2008-02-01 00:00:00 to 2008-02-02 00:00:00', '2008-03-01 00:00:00 to 2008-03-02 00:00:00']

        Ensure that if an event has no rule, that it appears only once.

        >>> event = Event(start=datetime.datetime(2008,1,1,8,0), end=datetime.datetime(2008,1,1,9,0))
        >>> occurrences = event.get_occurrences(datetime.datetime(2008,1,24), datetime.datetime(2008,3,2))
        >>> ["%s to %s" %(o.start, o.end) for o in occurrences]
        []

        """
        persisted_occurrences = self.occurrence_set.all()
        occ_replacer = OccurrenceReplacer(persisted_occurrences)
        occurrences = self._get_occurrence_list(start, end)
        final_occurrences = []
        for occ in occurrences:
            # replace occurrences with their persisted counterparts
            if occ_replacer.has_occurrence(occ):
                p_occ = occ_replacer.get_occurrence(occ)
                # ...but only if they are within this period
                if p_occ.start < end and p_occ.end >= start:
                    final_occurrences.append(p_occ)
            else:
              final_occurrences.append(occ)
        # then add persisted occurrences which originated outside of this period but now
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
            goodfriday = rrule.rrule(rrule.YEARLY, dtstart=self.start, byeaster=-2)
            christmas = rrule.rrule(rrule.YEARLY, dtstart=self.start, bymonth=12, bymonthday=25)
            set.exrule(goodfriday)
            set.exrule(christmas)
            return set

    def _create_occurrence(self, start, end=None):
        if end is None:
            end = start + (self.end - self.start)
        occ = Occurrence(event=self,start=start,end=end, original_start=start, original_end=end)
        if self.info.cluster_by_week and self != self.info.primary_generator():
            epoch = occ.start - self.start # diff from generator start
            prototype_date = self.info.primary_generator().start + epoch
            occ.prototype = self.info.primary_generator().get_occurrence(prototype_date)
        return occ

    def get_occurrence(self, date):
        rule = self.get_rrule_object()
        if rule:
            next_occurrence = rule.after(date, inc=True)
        else:
            next_occurrence = self.start
        if next_occurrence == date:
            try:
                return Occurrence.objects.get(event = self, original_start = date)
            except Occurrence.DoesNotExist:
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
        returns a generator that produces unpersisted occurrences after the
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
        ``after``.	Includes all of the persisted Occurrences.
        """
        occ_replacer = OccurrenceReplacer(self.occurrence_set.all())
        generator = self._occurrences_after_generator(after)
        while True:
            next = generator.next()
            yield occ_replacer.get_occurrence(next)


class OccurrenceBase(models.Model):
    # explicit fields
    original_start = models.DateTimeField(_("original start"))
    original_end = models.DateTimeField(_("original end"))
    start = models.DateTimeField(_("start"))
    end = models.DateTimeField(_("end"))
    cancelled = models.BooleanField(_("cancelled"), default=False)

#     # variation fields
#     varied_title = models.CharField("Title", max_length=255, blank=True, null=True)
#     varied_subtitle = models.CharField("Subtitle", max_length=255, blank=True)
#     varied_description = models.TextField("Description", blank=True, null=True, help_text=MARKUP_HELP)
#     varied_venue = models.ForeignKey(Venue, verbose_name="venue", blank=True, null=True)
#     varied_starts_at_venue = models.BooleanField("Starts at venue?")
#     varied_featured = models.BooleanField("Featured?")
#     varied_auslan = models.BooleanField("Presented in Auslan?")
#     varied_exhibition = models.ForeignKey('whats_on.Exhibition', verbose_name="Exhibition", blank=True, null=True)
#     varied_contact = models.ForeignKey('generic.ContactDetail', verbose_name="Contact", null=True, blank=True)
#     varied_language = models.CharField("Language", max_length=5, choices=LANGUAGES, default="en", help_text="Please note, this refers to the written (not spoken) language, so both Mandarin and Cantonese use Simplified Chinese")
#     varied_translated_description = models.TextField("Translated desription", blank=True)
#     varied_poster_image = models.ImageField(blank=True, upload_to="occurrence_images/canonical/")
# #    varied_photos = models.ManyToManyField('generic.MiscellaneousPhoto', verbose_name="Photos", blank=True, null=True)

    class Meta:
        verbose_name = _("occurrence")
        verbose_name_plural = _("occurrences")

# # Jesus wept!
# # There must be a smarter, more pythonic way of doing this!
#     def title(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.title()
#         if self.varied_title:
#             return self.varied_title
#         else:
#             return self.event.info.title
# 
#     def subtitle(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.subtitle()
#         if self.varied_subtitle:
#             return self.varied_subtitle
#         else:
#             return self.event.info.subtitle
# 
#     def description(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.description()
#         if self.varied_description:
#             return self.varied_description
#         else:
#             return self.event.info.description
#     
#     def venue(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.venue()
#         if self.varied_venue:
#             return self.varied_venue
#         else:
#             return self.event.info.venue
#     
#     def starts_at_venue(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.starts_at_venue()
#         if self.varied_starts_at_venue:
#             return self.varied_starts_at_venue
#         else:
#             return self.event.info.starts_at_venue
#     
#     def featured(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.featured()
#         if self.varied_featured:
#             return self.varied_featured
#         else:
#             return self.event.info.featured
#     
#     def auslan(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.auslan()
#         if self.varied_auslan:
#             return self.varied_auslan
#         else:
#             return self.event.info.auslan
#     
#     def exhibition(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.exhibition()
#         if self.varied_exhibition:
#             return self.varied_exhibition
#         else:
#             return self.event.info.exhibition
#     
#     def contact(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.contact()
#         if self.varied_contact:
#             return self.varied_contact
#         else:
#             return self.event.info.contact
#     
#     def language(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.language()
#         if self.varied_language:
#             return self.varied_language
#         else:
#             return self.event.info.language
#     
#     def translated_description(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.description()
#         if self.varied_translated_description:
#             return self.varied_translated_description
#         else:
#             return self.event.info.translated_description
#     
#     def poster_image(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.poster_image()
#         if self.varied_poster_image:
#             return self.varied_poster_image
#         else:
#             return self.event.info.poster_image
#     
#     def occurrence_poster_image(self):
#         if self.event.info.cluster_by_week and self.event != self.event.info.primary_generator():
#             return self.prototype.varied_poster_image
#         else:
#             return self.varied_poster_image
#     
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

#     def get_absolute_url(self):
#         if self.pk is not None:
#             return reverse('occurrence', kwargs={'occurrence_id': self.pk,
#                 'event_id': self.event.id})
#         return reverse('occurrence_by_date', kwargs={
#             'event_id': self.event.id,
#             'year': self.start.year,
#             'month': self.start.month,
#             'day': self.start.day,
#             'hour': self.start.hour,
#             'minute': self.start.minute,
#             'second': self.start.second,
#         })
# 
#     def get_cancel_url(self):
#         if self.pk is not None:
#             return reverse('cancel_occurrence', kwargs={'occurrence_id': self.pk,
#                 'event_id': self.event.id})
#         return reverse('cancel_occurrence_by_date', kwargs={
#             'event_id': self.event.id,
#             'year': self.start.year,
#             'month': self.start.month,
#             'day': self.start.day,
#             'hour': self.start.hour,
#             'minute': self.start.minute,
#             'second': self.start.second,
#         })
# 
#     def get_edit_url(self):
#         if self.pk is not None:
#             return reverse('edit_occurrence', kwargs={'occurrence_id': self.pk,
#                 'event_id': self.event.id})
#         return reverse('edit_occurrence_by_date', kwargs={
#             'event_id': self.event.id,
#             'year': self.start.year,
#             'month': self.start.month,
#             'day': self.start.day,
#             'hour': self.start.hour,
#             'minute': self.start.minute,
#             'second': self.start.second,
#         })

    def __unicode__(self):
        return ugettext("%(event)s: %(day)s") % {
            'event': self.generator.event.title,
            'day': self.start.strftime('%a, %d %b %Y'),
        }

    def __cmp__(self, other):
        rank = cmp(self.start, other.start)
        if rank == 0:
            return cmp(self.end, other.end)
        return rank

    def __eq__(self, other):
        return self.event == other.event and self.original_start == other.original_start and self.original_end == other.original_end
