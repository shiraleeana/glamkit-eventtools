Glamkit-schedule
===============

An event management application designed for the GLAM (Galleries, Libraries, Museums and Archives) sector. It is a fork of the popular django-schedule app, featuring:

 * one-time and recurring events
 * calendar exceptions (occurrences changed or cancelled)
 * occurrences accessible through Event API, Period API and Django Admin
 * ready to use, nice user interface
 * flexible calendar template tags
 * project sample which can be launched immediately and reused in your project

Installation
------------

Download the code; put in into your project's directory or run <pre>python setup.py install</pre> to install system-wide.

REQUIREMENTS: python-vobject (comes with most distribution as a package).

Settings.py
-----------

REQUIRED
^^^^^^^^

`INSTALLED_APPS` - add: 
    'schedule',

`TEMPLATE_CONTEXT_PROCESSORS` - add:
    "django.core.context_processors.request",

Optional
^^^^^^^^

`FIRST_DAY_OF_WEEK`

This setting determines which day of the week your calendar begins on if your locale doesn't already set it. Default is 0, which is Sunday.

[[[[OCCURRENCE_CANCEL_REDIRECT

This setting controls the behavior of :func:`Views.get_next_url`. If set, all calendar modifications will redirect here (unless there is a `next` set in the request.)]]]]

SHOW_CANCELLED_OCCURRENCES

This setting controls the behavior of :func:`Period.classify_occurence`. If True, then occurences that have been cancelled will be displayed with a css class of cancelled, otherwise they won't appear at all.

Defaults to False

