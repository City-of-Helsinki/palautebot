import requests
from django.conf import settings


# This function sends the feedback to the Helsinki feedback API
def create_ticket(source, feedback):
    feedback['api_key'] = settings.OPEN311_API_KEY
    feedback['service_code'] = settings.OPEN311_API_SERVICE_CODE
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response_new_ticket = requests.post(
        settings.OPEN311_POST_API_URL, data=feedback, headers=headers)
    url_to_feedback = ''
    new_ticket = response_new_ticket.json()
    print(new_ticket)
    for entry in new_ticket:
        if 'code' in entry:
            print('ERROR: ', entry['code'])
            print('info: ', entry['description'])
            return url_to_feedback
        elif 'service_request_id' in entry:
            break
        else:
            print('something wrong with api data')
            print(entry)
            return url_to_feedback
    try:
        new_ticket_id = new_ticket[0]['service_request_id']
        url_to_feedback = 'https://www.hel.fi/helsinki/fi/kaupunki-ja-hallinto/osallistu-ja-vaikuta/palaute/nayta-palaute?fid=%s' % (new_ticket_id)  # noqa
    except KeyError as e:
        print('New data doesn\'t contain service_request_id %s' % (new_ticket))
    return url_to_feedback
