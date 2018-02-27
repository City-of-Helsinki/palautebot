import logging

from django.core.management.base import BaseCommand

from feedback.ticket_updates import handle_ticket_updates

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Check and handle Open311 ticket updates'

    def handle(self, *args, **options):
        logger.info('Handling ticket updates...')

        handle_ticket_updates()

        logger.info('Done.')
