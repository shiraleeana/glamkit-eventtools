from django.contrib import admin
# 
from events.models import Rule
# 
# class CalendarAdminOptions(admin.ModelAdmin):
#     prepopulated_fields = {"slug": ("name",)}
#     search_fields = ['name']
# 
# 
# admin.site.register(Calendar, CalendarAdminOptions)
# admin.site.register([Rule, Event, CalendarRelation])
admin.site.register(Rule)