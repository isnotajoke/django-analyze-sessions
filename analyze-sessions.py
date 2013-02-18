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
        for session in self.get_sessions():
            self.process_session(session)

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

    def get_filtered_queryset(self):
        """
        Return a Session qs with any configured filters already applied.
        """
        # XXX: Potentially MySQL-specific. Should be revised to handle
        #      other DBMS, or fail gracefully when they're in use.
        return Session.objects.extra(where=['LENGTH(session_data) > %d' % self.bigger_than])

    def get_sessions(self):
        """
        Return sessions that match the configured bigger than parameters.

        Internally, collect sessions in batches of size batch_size, then yield
        to the caller.
        """
        start = 0
        while True:
            qs = self.get_filtered_queryset()
            if qs.count() == 0:
                return

            qs = qs[start:start+self.batch_size]
            start += self.batch_size

            for session in qs:
                yield session

    def process_session(self, session):
        """
        Process a session.
        """
        pass
