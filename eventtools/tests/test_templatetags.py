# import datetime
# 
# from django.test import TestCase
# 
# from events.templatetags.eventstags import querystring_for_date
# 
# class TestTemplateTags(TestCase):
#     
#     def test_querystring_for_datetime(self):
#         date = datetime.datetime(2008,1,1,0,0,0)
#         query_string=querystring_for_date(date)
#         self.assertEqual("?year=2008&month=1&day=1&hour=0&minute=0&second=0",
#             query_string)

from datetime import date
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from calendartest.calander.templatetags.month_calendar import event_calendar

class CalendarTest(TestCase):
    "Class to test month_calendar.event_calendar"
    
    TIME_RANGE = 3
    CALENDAR_SIZE = 35
    START_DATE = date.today()
    END_DATE = START_DATE + relativedelta(days=TIME_RANGE)
    
    def setUp(self):
        self.calendar = event_calendar(self.__class__.START_DATE, self.__class__.END_DATE)
        
    def test_calendar_size(self):
        day_count = 0
        
        for week in self.calendar['calendar']:
            for day in week:
                day_count += 1
                
        self.assertEqual(day_count, self.__class__.CALENDAR_SIZE, 
                        'Incorrect calendar size')
        
    def test_active_days(self):
        active_days = 0
        
        for week in self.calendar['calendar']:
            for day in week:
                if 'active_day' in day['classes']:
                    active_days += 1
                    
        self.assertEqual(active_days, self.__class__.TIME_RANGE, 'Incorrect active day count')
        
    def test_prev_next(self):
        prev = self.__class__.START_DATE + relativedelta(months=-1)
        next = self.__class__.START_DATE + relativedelta(months=+1)
        
        self.assert_(self.calendar['prev'] == prev and self.calendar['next'] == next,
                     'Incorrect previous/next month')
        
