
# -*- coding: utf-8 -*-

from project.settings import *

SECRET_KEY = '!'

DEBUG = True

INTERNAL_IPS = ('127.0.0.1',)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s %(data)s'
        },
        'normal': {
            'format': '%(asctime)s %(levelname)s %(name)s %(thread)d %(lineno)s %(message)s %(data)s'
        },
    },
    'filters': {
        'default': {
            '()': 'project.logging_helpers.Filter',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'verbose',
            'filters': ['default'],
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'formatter': 'verbose',
        },
        'palautebot': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'formatter': 'verbose',
        },
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
            'formatter': 'verbose',
        },
    },
}

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

