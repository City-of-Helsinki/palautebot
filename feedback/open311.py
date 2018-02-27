from copy import deepcopy

import requests
from django.conf import settings

from .utils import check_required_settings

REQUIRED_SETTINGS_POST = ('OPEN311_API_KEY', 'OPEN311_API_SERVICE_CODE', 'OPEN311_API_BASE_URL')
REQUIRED_SETTINGS_GET = ('OPEN311_API_BASE_URL',)


class Open311Exception(Exception):
    pass


def _get_api_base_url():
    url = settings.OPEN311_API_BASE_URL
    if not url.endswith('/'):
        url += '/'
    return url


# This function sends the feedback to the Helsinki feedback API
def create_ticket(feedback):
    feedback = deepcopy(feedback)

    feedback['api_key'] = settings.OPEN311_API_KEY
    feedback['service_code'] = settings.OPEN311_API_SERVICE_CODE

    try:
        new_ticket = post_service_request_to_api(feedback)
    except requests.RequestException as e:
        raise Open311Exception(e)

    for entry in new_ticket:
        if 'code' in entry:
            raise Open311Exception(
                'Got error code {}, description: {}'.format(entry['code'], entry['description'])
            )
        elif 'service_request_id' in entry:
            break
        else:
            raise Open311Exception('Something wrong with api data, entry: {}'.format(entry))
    try:
        new_ticket_id = new_ticket[0]['service_request_id']
    except KeyError:
        raise Open311Exception("New data doesn't contain service_request_id, ticket {}".format(new_ticket))
    return new_ticket_id


def post_service_request_to_api(data):
    check_required_settings(REQUIRED_SETTINGS_POST)

    try:
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post('{}requests.json'.format(_get_api_base_url()), data=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Open311Exception(e)


def get_service_request_from_api(ticket_id):
    check_required_settings(REQUIRED_SETTINGS_GET)

    try:
        response = requests.get('{}requests/{}.json'.format(_get_api_base_url(), ticket_id))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise Open311Exception(e)
