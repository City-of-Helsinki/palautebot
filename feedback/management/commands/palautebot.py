import logging

from django.core.management.base import BaseCommand

from feedback.twitter import TwitterHandler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        logger.info('Running Palautebot')

        twitter_handler = TwitterHandler()
        twitter_handler.run()
