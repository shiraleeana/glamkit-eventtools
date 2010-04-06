from eventtools.models import EventBase, EventVariationBase
from django.db import models

class LectureEvent(EventBase):
    lecturer = models.TextField(max_length=100)
    location = models.TextField(max_length=100)

class LectureEventVariation(EventVariationBase):
    unvaried_event = models.ForeignKey(LectureEvent)
    #Usually nothing should be compulsory in a variation (but you never know)
    title = models.CharField(max_length=100, blank=True)
    location = models.TextField(max_length=100, blank=True)

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
            
class BroadcastEventVariation(EventVariationBase):
    unvaried_event = models.ForeignKey(BroadcastEvent)
    
    presenter = models.TextField(max_length=100, blank=True)
    reason_for_variation = models.TextField()
        
class LessonEvent(EventBase):
    subject = models.TextField(max_length=100)
    #Test that an event can survive without variation