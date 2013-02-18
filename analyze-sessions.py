from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    args = '--batch-size=n --bigger-than=n'
    help = 'Analyze Django sessions, summarizing present keys & session size'

    # Number of sessions to process in one batch.
    # Tune as necessary to get DB load at a sweet spot.
    batch_size = 5000

    # Only process sessions with more than this many bytes.
    bigger_than = 10 * 1024

    def handle(self, *args, **options):
        # process options.
        self.process_options(**options)

        # process sessions

    def process_options(self, options):
        """
        Validate options & configure self appropriately based on option
        settings
        """
        if 'batch-size' in options:
            try:
                new_batch_size = int(options['batch-size'])
            except ValueError, e:
                raise CommandError('batch-size must be a positive integer')

            self.batch_size = new_batch_size

            if self.batch_size <= 0:
                raise CommandError('batch-size must be a positive integer')

        if 'bigger-than' in options:
            try:
                new_bigger_than = int(options['bigger-than'])
            except ValueError, e:
                raise CommandError('bigger-than must be an integer')

            self.bigger_than = new_bigger_than
