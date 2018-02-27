from datetime import timedelta
from unittest import mock

import pytest
from django.utils.timezone import now

from feedback.models import Feedback, Tweet
from feedback.tests.utils import SubstringMatcher
from feedback.ticket_updates import handle_ticket_updates


@pytest.mark.parametrize('answer', (
    'foobar',
    'foobar' * 100,
))
@mock.patch('feedback.twitter.TwitterHandler.answer_to_tweet')
@pytest.mark.django_db
def test_ticket_updates_success(answer_to_tweet, answer):
    tweet = Tweet.objects.create(source_id='777', source_created_at=now(), user_identifier='fooman')
    feedback = Feedback.objects.create(ticket_id='abc123', tweet=tweet)
    assert feedback.current_comment == ''

    with mock.patch('feedback.ticket_updates.get_service_request_from_api',
                    return_value=[{'status_notes': answer}]):
        handle_ticket_updates()

    answer_to_tweet.assert_called_with('777', SubstringMatcher('@fooman palautteeseesi on vastattu:\n'))
    if len(answer) <= 280:
        answer_to_tweet.assert_called_with('777', SubstringMatcher(answer))
    else:
        answer_to_tweet.assert_called_with('777', SubstringMatcher(answer[:100]))
        answer_to_tweet.assert_called_with('777', SubstringMatcher('...'))
        answer_to_tweet.assert_called_with('777', SubstringMatcher(feedback.get_url()))

    feedback.refresh_from_db()
    assert feedback.current_comment == answer


@pytest.mark.parametrize('answer', (
    None,
    '',
    'foo',
))
@mock.patch('feedback.twitter.TwitterHandler.answer_to_tweet')
@pytest.mark.django_db
def test_ticket_updates_no_change(answer_to_tweet, answer):
    tweet = Tweet.objects.create(source_id='777', source_created_at=now(), user_identifier='fooman')
    feedback = Feedback.objects.create(ticket_id='abc123', tweet=tweet, current_comment=answer or '')

    with mock.patch('feedback.ticket_updates.get_service_request_from_api',
                    return_value=[{'status_notes': answer}]):
        handle_ticket_updates()

    answer_to_tweet.assert_not_called()
    feedback.refresh_from_db()
    assert feedback.current_comment == (answer or '')


@mock.patch('feedback.twitter.TwitterHandler.answer_to_tweet')
@pytest.mark.django_db
def test_ticket_updates_too_old_ticket_ignored(answer_to_tweet,):
    tweet = Tweet.objects.create(source_id='777', source_created_at=now(), user_identifier='fooman')
    feedback = Feedback.objects.create(ticket_id='abc123', tweet=tweet)
    Feedback.objects.filter(id=feedback.id).update(modified_at=now() - timedelta(days=33))

    with mock.patch('feedback.ticket_updates.get_service_request_from_api',
                    return_value=[{'status_notes': 'foobar'}]):
        handle_ticket_updates()

    answer_to_tweet.assert_not_called()
