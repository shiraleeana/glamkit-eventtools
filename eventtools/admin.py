from django.contrib import admin
from eventtools.models import Rule
from eventtools.adminviews import occurrences, make_exceptional_occurrence
from django.conf.urls.defaults import *
from django.core import urlresolvers


admin.site.register(Rule)

class EventAdminBase(admin.ModelAdmin):
    """
    Need to add views:
    - to view the (generated and exceptional) accurrences
    - to make an exception to a particular generated view
    """
    def get_urls(self):
        super_urls = super(EventAdminBase, self).get_urls()
        my_urls = patterns('',
            url(r'^(?P<id>\d+)/occurrences/$', self.admin_site.admin_view(occurrences), {'modeladmin': self}),
              url(r'^(?P<event_id>\d+)/create_exception/(?P<gen_id>\d+)/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})/(?P<hour>\d{1,2})-(?P<minute>\d{2})-(?P<second>\d{2})/$', self.admin_site.admin_view(make_exceptional_occurrence), {'modeladmin': self}),
        )
        return my_urls + super_urls
    list_display = ('title', 'edit_occurrences_link',)


class OccurrenceAdminBase(admin.ModelAdmin):
    
    exclude = ('generator', 'unvaried_end_date', 'unvaried_end_time', 'unvaried_start_date', 'unvaried_start_time', 'cancelled')

    def change_view(self, request, object_id, extra_context=None):
        """
        Not sure what this does that isn't part of the default?
        """        
        result = super(OccurrenceAdminBase, self).change_view(request, object_id, extra_context)
        if not request.POST.has_key('_addanother') and not request.POST.has_key('_continue'):
            
            OccurrenceModel = self.model
            occ = OccurrenceModel.objects.get(pk=object_id)
            
            app_label = OccurrenceModel._meta.app_label
            # import pdb; pdb.set_trace()
            event_model_label = occ.generator.event.__class__.__name__
            
            event_change_url = urlresolvers.reverse(('admin:%s_%s_change' % (app_label, event_model_label)).lower(), args=(occ.generator.event.id,))
            
            occ_list_url = "%soccurrences/" % event_change_url
            result['Location'] = occ_list_url
        return result

   # list_display = ('title', 'event', 'original_start')
    ordering = ('varied_start_date', 'varied_start_time')
