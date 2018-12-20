import logging
from datetime import timedelta

from django.conf import settings
from django.utils.timezone import now

from .models import Feedback
from .open311 import Open311Exception, get_service_request_from_api
from .twitter import TwitterHandler

logger = logging.getLogger(__name__)

TWITTER_MESSAGE_MAX_CHARS = 280

# this value should be actually read from the twitter API once a day (atm it is 23),
# but it is easier to just use a bit larger static value
TWITTER_SHORT_URL_LENGTH = 30


def parse_answer(status_notes, user_identifier, url):
    answer_base = '@{} Palautteeseesi on vastattu:\n{}'.format(user_identifier, status_notes)
    line_with_url = '\n' + url
    # Put link to feedback system at the end to make it tweet's main link
    answer = answer_base + line_with_url
    if len(answer) > TWITTER_MESSAGE_MAX_CHARS:
        # truncate the response
        char_count = TWITTER_MESSAGE_MAX_CHARS - len(line_with_url) - 3  # 3 dots
        answer = '{}...'.format(answer_base[:char_count]) + line_with_url
    return answer


def handle_ticket_updates():
    twitter_handler = TwitterHandler()

    start_timestamp = now() - timedelta(hours=settings.OPEN311_TICKET_POLLING_TIME)
    feedbacks = Feedback.objects.filter(modified_at__gte=start_timestamp)
    logger.debug('Checking updates for {} feedback items'.format(len(feedbacks)))

    for feedback in feedbacks:
        try:
            data = get_service_request_from_api(feedback.ticket_id)
        except Open311Exception as e:
            logger.error('Cannot fetch data of ticket {}, exception: {}'.format(feedback.ticket_id, e))
            continue
        if not data:
            logger.error('Cannot fetch data of ticket {}, got empty response'.format(feedback.ticket_id))
            continue

        logger.debug('Fetched data for ticket {}: {}'.format(feedback.ticket_id, data))

        try:
            status_notes = data[0]['status_notes'] or ''
        except (KeyError, IndexError, TypeError):
            logger.error('Got invalid response: {}'.format(data))
            continue

        if status_notes != feedback.current_comment:
            logger.info('Feedback {} status notes changed from "{}" to "{}"'.format(
                feedback.ticket_id, feedback.current_comment, status_notes))
            feedback.current_comment = status_notes
            feedback.save()

            answer = parse_answer(status_notes, feedback.tweet.user_identifier, feedback.get_url())
            twitter_handler.answer_to_tweet(feedback.tweet.source_id, answer)
