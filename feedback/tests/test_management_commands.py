from unittest import mock

from django.core.management import call_command


@mock.patch('feedback.twitter.handle_twitter')
def test_palautebot_management_command(handle_twitter):
    call_command('palautebot')
    handle_twitter.assert_called_with()
