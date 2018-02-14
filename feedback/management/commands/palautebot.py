import logging

from django.core.management.base import BaseCommand

from feedback.twitter import handle_twitter

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Palautebot runner management command'

    def handle(self, *args, **options):
        logger.info('Running Palautebot')
        handle_twitter()
