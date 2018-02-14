from copy import deepcopy
from unittest import mock

import pytest
from django.core.exceptions import ImproperlyConfigured

from feedback.open311 import create_ticket


@pytest.mark.parametrize('required_setting', (
    'OPEN311_API_KEY',
    'OPEN311_API_SERVICE_CODE',
    'OPEN311_POST_API_URL',
))
def test_create_ticket_required_settings(settings, required_setting, expected_parsed_data):
    setattr(settings, required_setting, '')

    with pytest.raises(ImproperlyConfigured) as e_info:
        create_ticket(expected_parsed_data)

    assert str(e_info.value) == 'Setting {} is not set'.format(required_setting)


@mock.patch('feedback.open311.requests.post')
def test_create_ticket(post, expected_parsed_data):
    create_ticket(expected_parsed_data)

    data = deepcopy(expected_parsed_data)
    data.update(
        service_code='test_OPEN311_API_SERVICE_CODE',
        api_key='test_OPEN311_API_KEY',
    )

    post.assert_called_with(
        'http://test_OPEN311_POST_API_URL',
        data=data,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
    )

# TODO moar tests
