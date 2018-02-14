from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def check_required_settings(required_settings):
    for required_setting in required_settings:
        if not getattr(settings, required_setting, None):
            raise ImproperlyConfigured('Setting {} is not set'.format(required_setting))
