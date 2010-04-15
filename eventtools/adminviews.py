from django.shortcuts import render_to_response, get_object_or_404
from whats_on.models import Event, Rule, OccurrenceGenerator, Occurrence
from whats_on.periods import Month
from django.template import RequestContext
from django.http import HttpResponseRedirect
import datetime
from django.core import urlresolvers
# from whats_on.forms import OccurrenceForm
from django.utils.translation import ugettext as _

def occurrences(request, id):
    event = EventInfo.objects.get(pk=id)
    generators = event.generators.all()
    first = event.get_first_occurrence()
    last = event.get_last_day()
    if 'year' in request.GET and 'month' in request.GET:
        period = Month(generators, datetime.datetime(int(request.GET.get('year')),int(request.GET.get('month')),1))
    else:
        now = datetime.datetime.now()
        if first > now:
            period = Month(generators, first)
        else:
            period = Month(generators, now)
    hasprev = first < period.start
    if not last:
        hasnext = True
    else:
        hasnext = last > period.end 
    occurrences = period.get_occurrences()
    title = _("Select an occurrence to change")
    return render_to_response('admin/whats_on/list_occurrences.html', {"event": event, 'occurrences': occurrences, 'period': period, 'hasprev': hasprev, 'hasnext': hasnext, 'title': title}, context_instance=RequestContext(request))

# def edit_occurrence(request, event_id, info_id, 
#          template_name="admin/whats_on/edit_occurrence.html", *args, **kwargs):
#          event, occurrence = get_occurrence(event_id, *args, **kwargs)
#          form = OccurrenceForm(data=request.POST or None, instance=occurrence)
#          if form.is_valid():
#           occurrence = form.save(commit=False)
#           occurrence.event = event
#           occurrence.save()
#           return HttpResponseRedirect('../../../../../../../../')
#          return render_to_response(template_name, {
#           'adminform': form,
#           'occurrence': occurrence,
#          }, context_instance=RequestContext(request))

def persist_occurrence(request, event_id, info_id, year, month, day, hour, minute, second):
    event = get_object_or_404(OccurrenceGenerator, id=event_id)
    occurrence = event.get_occurrence(datetime.datetime(int(year), int(month), int(day), int(hour), int(minute), int(second)))
    if occurrence is None:
        raise Http404
    occurrence.save()
    change_url = urlresolvers.reverse('admin:whats_on_occurrence_change', args=(occurrence.id,))
    return HttpResponseRedirect(change_url)

# def get_occurrence(event_id, occurrence_id=None, year=None, month=None,
#       day=None, hour=None, minute=None, second=None):
#       """
#       Because occurrences don't have to be persisted, there must be two ways to
#       retrieve them. both need an event, but if its persisted the occurrence can
#       be retrieved with an id. If it is not persisted it takes a date to
#       retrieve it.	This function returns an event and occurrence regardless of
#       which method is used.
#       """
#       if(occurrence_id):
#             occurrence = get_object_or_404(Occurrence, id=occurrence_id)
#             event = occurrence.event
#       elif(all((year, month, day, hour, minute, second))):
#             event = get_object_or_404(OccurrenceGenerator, id=event_id)
#             occurrence = event.get_occurrence(
#                 datetime.datetime(int(year), int(month), int(day), int(hour),
#                   int(minute), int(second)))
#             if occurrence is None:
#                  raise Http404
#       else:
#             raise Http404
#       return event, occurrence
