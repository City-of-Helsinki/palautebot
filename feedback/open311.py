import logging
from copy import deepcopy

import requests
from django.conf import settings

from .utils import check_required_settings

REQUIRED_SETTINGS = ('OPEN311_API_KEY', 'OPEN311_API_SERVICE_CODE', 'OPEN311_POST_API_URL')

logger = logging.getLogger(__name__)


class Open311Exception(Exception):
    pass


def post_to_api(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(settings.OPEN311_POST_API_URL, data=data, headers=headers)
    return response.json()


# This function sends the feedback to the Helsinki feedback API
def create_ticket(feedback):
    check_required_settings(REQUIRED_SETTINGS)
    feedback = deepcopy(feedback)

    feedback['api_key'] = settings.OPEN311_API_KEY
    feedback['service_code'] = settings.OPEN311_API_SERVICE_CODE

    new_ticket = post_to_api(feedback)

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
        url_to_feedback = (
            'https://www.hel.fi/helsinki/fi/kaupunki-ja-hallinto/osallistu-ja-vaikuta/palaute/nayta-palaute?fid=%s'
            % new_ticket_id
        )
    except KeyError:
        raise Open311Exception("New data doesn't contain service_request_id, ticket {}".format(new_ticket))
    return {'ticket_id': new_ticket_id, 'ticket_url': url_to_feedback}
