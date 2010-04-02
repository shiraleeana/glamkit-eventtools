#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
 
setup(
    name='glamkit-events',
    version='0.5b',
    description='An event management app for Django.',
    author='Thomas Ashelford',
    author_email='thomas@interaction.net.au',
    url='http://github.com/glamkit/glamkit-events/tree/master',
    packages=[
        'events',
        'events.feeds',
        'events.management',
        'events.management.commands',
        'events.models',
        'events.templatetags',
        'events.tests',
    ],
    include_package_data=True,
    zip_safe=False,
    classifiers=['Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Topic :: Utilities'],
    install_requires=['setuptools', 'vobject', 'python-dateutil'],
    license='BSD',
    test_suite = "events.tests",
)
