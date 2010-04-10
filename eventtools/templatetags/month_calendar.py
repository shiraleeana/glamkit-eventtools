import calendar
from datetime import date, timedelta
from dateutil.relativedelta import *
from django import template

register = template.Library()

def month_calendar(start=None, end=None):
    """
    Creates a configurable html calendar
    
    It takes two optional arguments:
    
    start
    """
    cal = calendar.Calendar(6)
    if not start:
        start = date.today()
    if not end:
        end = start
        
    # Return a list of the weeks in the month month of the year as full weeks. Weeks are lists of seven day numbers
    month = cal.monthdatescalendar(start.year, start.month)
    
    today = date.today()
    
    # annotate each day with a list of class names that describes their status in the calendar - not_in_month, today, selected
    def annotate(day):
        classes = []
        if day.month != start.month:
            classes.append('not_in_month')
        if day == today:
            classes.append('today')
        if end > day >= start:
            classes.append('selected')
        return {'date': day, 'classes': classes}
    days = [map(annotate, week) for week in month]
    links = {'prev': start+relativedelta(months=-1), 'next': start+relativedelta(months=+1)
    print month
    print start
    print today
    print links
    
    return {'month': days, 'start': start, 'today': today, 'links': links}

register.inclusion_tag('whatson/calendar.html')(event_calendar)