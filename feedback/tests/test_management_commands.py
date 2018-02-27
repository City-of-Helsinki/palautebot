from unittest import mock

from django.core.management import call_command


@mock.patch('feedback.twitter.TwitterHandler.run')
def test_handle_twitter_feedback_management_command(run):
    call_command('handle_twitter_feedback')
    run.assert_called_with()


@mock.patch('feedback.ticket_updates.handle_ticket_updates')
def test_handle_ticket_updates_management_command(handle_ticket_updates):
    call_command('handle_ticket_updates')
    handle_ticket_updates.assert_called_with()
