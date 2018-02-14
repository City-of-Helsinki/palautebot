from django.core.management.base import BaseCommand

from feedback.twitter import handle_twitter


class Command(BaseCommand):
    help = 'Palautebot runner management command'

# This is the main method
    def handle(self, *args, **options):
        handle_twitter()
