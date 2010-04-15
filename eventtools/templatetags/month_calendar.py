import calendar
from datetime import date, timedelta
from dateutil.relativedelta import *
from django import template

register = template.Library()

def month_calendar(month=None, week_start=6, selected_start=None, selected_end=None):
    """
    Creates a configurable html calendar displaying one month
    
    It takes four optional arguments:
    
    month: a date object representing the month to be displayed (ie. it needs to be a date within the month to be displayed).
    selected_start:
    selected_end:
    """
    
    cal = calendar.Calendar(week_start)
    today = date.today()
    if not month:
        month = date.today()
    if not selected_end:
        selected_end = selected_start
        
    # month_calendar is a list of the weeks in the month of the year as full weeks. Weeks are lists of seven day numbers
    month_calendar = cal.monthdatescalendar(month.year, month.month)
    
    
    # annotate each day with a list of class names that describes their status in the calendar - not_in_month, today, selected
    def annotate(day):
        classes = []
        if day.month != month.month:
            classes.append('not_in_month')
        if day == today:
            classes.append('today')
        if selected_start:
            if selected_end > day >= selected_start:
                classes.append('selected')
        return {'date': day, 'classes': classes}
    month_calendar = [map(annotate, week) for week in month_calendar]
    links = {'prev': month+relativedelta(months=-1), 'next': month+relativedelta(months=+1)}
    
    return {'month': month, 'month_calendar': month_calendar, 'today': today, 'links': links}

register.inclusion_tag('month_calendar.html')(month_calendar)

def annotated_day(day, classes=None):
    return {'day': day, 'classes': classes}
register.inclusion_tag('annotated_day.html')(annotated_day)
