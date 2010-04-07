from eventtools.models import EventBase
from django.db import models

class LectureEvent(EventBase):
    lecturer = models.TextField(max_length=100)
    location = models.TextField(max_length=100)
    wheelchair_access = models.BooleanField(default=True)
    varied_by = "LectureEventVariation"

class LectureEventVariation(models.Model):
#     unvaried_event = models.ForeignKey(LectureEvent)
    #Usually nothing should be compulsory in a variation (but you never know)
    title = models.CharField(max_length=100, blank=True, null=True)
    location = models.TextField(max_length=100, blank=True, null=True)
    wheelchair_access = models.NullBooleanField() #implied default = None

# Not allowed
# 
# class LectureEventVariation2(EventVariationBase):
#     event = models.ForeignKey(LectureEvent)
#     #Usually nothing should be compulsory in a variation (but you never know)
#     title = models.CharField(max_length=100, blank=True)

# Not allowed
# class DinnerVariation(EventVariationBase):
#     pass
    


class BroadcastEvent(EventBase):
    presenter = models.TextField(max_length=100)
    varied_by = "BroadcastEventVariation"
            
class BroadcastEventVariation(models.Model):
#     unvaried_event = models.ForeignKey(BroadcastEvent)
    
    presenter = models.TextField(max_length=100, blank=True)
    reason_for_variation = models.TextField()
        
class LessonEvent(EventBase):
    subject = models.TextField(max_length=100)
    #Test that an event can survive without variation