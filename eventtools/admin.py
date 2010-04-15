from django.contrib import admin
from eventtools.models import Rule
from events.adminviews import occurrences, persist_occurrence
from django.conf.urls.defaults import patterns

admin.site.register(Rule)

class EventAdminBase(admin.ModelAdmin):
    def get_urls(self):
        urls = super(EventAdminBase, self).get_urls()
        my_urls = patterns('',
            (r'^(?P<id>\d+)/occurrences/$', self.admin_site.admin_view(occurrences)),
            (r'^(?P<info_id>\d+)/persist/(?P<event_id>\d+)/(?P<year>\d+)/(?P<month>\d+)/(?P<day>\d+)/(?P<hour>\d+)/(?P<minute>\d+)/(?P<second>\d+)/$', self.admin_site.admin_view(persist_occurrence)),
        )
        return my_urls + urls
    list_display = ('has_multiple_occurrences',)


class OccurrenceAdminBase(admin.ModelAdmin):
    def change_view(self, request, object_id, extra_context=None):
        result = super(OccurrenceAdminBase, self).change_view(request, object_id, extra_context)
        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue'):
            occ = Occurrence.objects.get(pk=object_id)
            occ_list_url = "%soccurrences/" % urlresolvers.reverse('admin:whats_on_eventinfo_change', args=(occ.event.info.id,))
            result['Location'] = occ_list_url
        return result

#    list_display = ('title','event', 'original_start')
    ordering = ('varied_start_date', 'varied_start_time')
