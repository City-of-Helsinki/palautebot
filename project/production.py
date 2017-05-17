
# -*- coding: utf-8 -*-

import os
from project.settings import *

# Enable sslify
SSLIFY_DISABLE = False

# Raven
RAVEN_CONFIG = {
    'dsn': os.environ.get('RAVEN_KEY', ''),
}

INSTALLED_APPS = INSTALLED_APPS + (
    'raven.contrib.django.raven_compat',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry', 'console' ],
    },
    'formatters': {
        'verbose': {
            'format': ('%(asctime)s [%(process)d] [%(levelname)s] ' +
                       'pathname=%(pathname)s lineno=%(lineno)s ' +
                       'funcname=%(funcName)s %(message)s'),
            'datefmt': '%Y-%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'django': {
            'level': 'ERROR',
            'handlers': ['console', ],
            'formatter': 'verbose',
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'palautebot': {
            'level': 'DEBUG',
            'handlers': ['console', 'sentry' ],
            'formatter': 'verbose',
        },
        '': {
            'level': 'WARNING',
            'handlers': ['console', 'sentry' ],
            'formatter': 'verbose',
        },
    },
}

# vim: tabstop=2 expandtab shiftwidth=2 softtabstop=2

