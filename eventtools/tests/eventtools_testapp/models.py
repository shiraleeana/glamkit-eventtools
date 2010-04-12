from eventtools.models import EventBase
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _


class LectureEvent(EventBase):
    title = models.CharField(_("Title"), max_length = 255)
    lecturer = models.TextField(max_length=100)
    location = models.TextField(max_length=100)
    wheelchair_access = models.BooleanField(default=True)
    varied_by = "LectureEventVariation"

class LectureEventVariation(models.Model):
    #Usually nothing should be compulsory in a variation (but you never know)
    title = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(max_length=100, blank=True, null=True)
    wheelchair_access = models.NullBooleanField() #implied default == None

class BroadcastEvent(EventBase):
    presenter = models.TextField(max_length=100)
    studio = models.IntegerField()
    varied_by = "BroadcastEventVariation"
            
class BroadcastEventVariation(models.Model):
    presenter = models.TextField(max_length=100, blank=True, null=True)
    reason_for_variation = models.TextField()
        
class LessonEvent(EventBase):
    subject = models.TextField(max_length=100)
    #Test that an event can work without variations defined