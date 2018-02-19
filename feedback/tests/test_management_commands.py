from unittest import mock

from django.core.management import call_command


@mock.patch('feedback.twitter.TwitterHandler.run')
def test_palautebot_management_command(run):
    call_command('palautebot')
    run.assert_called_with()
