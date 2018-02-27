import logging

from django.core.management.base import BaseCommand

from feedback.twitter import TwitterHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Handle Twitter feedback from tweets and direct messages (redirected tweets)'

    def handle(self, *args, **options):
        logger.info('Handling Twitter...')

        twitter_handler = TwitterHandler()
        twitter_handler.run()

        logger.info('Done.')
