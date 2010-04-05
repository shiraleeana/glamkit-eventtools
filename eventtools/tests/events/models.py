from eventtools.models import EventBase
from django.db import models

class TestEvent1(EventBase):
    location = models.TextField(max_length=100)

class TestEvent2(EventBase):
    presenter = models.TextField(max_length=100)
