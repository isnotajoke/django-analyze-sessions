from collections import defaultdict

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session

class Command(BaseCommand):
    args = '--batch-size=n --bigger-than=n'
    help = 'Analyze Django sessions, summarizing present keys & session size'

    # XXX: Most of these should be set at __init__, not as class-level
    # constants
    # Number of sessions to process in one batch.
    # Tune as necessary to get DB load at a sweet spot.
    batch_size = 5000

    # Only process sessions with more than this many bytes.
    bigger_than = 10 * 1024

    # Total # of matching sessions
    processed_session_count = 0

    # Total # of sessions in DB
    total_session_count = 0

    # Encoded data sizes for the sessions we looked at
    sizes = []

    # Observed keys (key => frequency)
    keys = defaultdict(int)

    def handle(self, *args, **options):
        # process options.
        self.process_options(options)

        # Count all sessions
        self.total_session_count = Session.objects.all().count()

        # process sessions
        for session in self.get_sessions():
            self.process_session(session)

        # summarize results and exit
        self.print_results()

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
            if qs.count() == 0 or start >= qs.count():
                return

            qs = qs[start:start+self.batch_size]
            start += self.batch_size

            for session in qs:
                yield session

    def process_session(self, session):
        """
        Process a session.
        """
        self.processed_session_count += 1

        data = session.session_data
        self.sizes.append(len(data))

        decoded = session.get_decoded()
        for key in decoded:
            self.keys[key] += 1

    def print_results(self):
        self.stdout.write("Processed %d sessions out of %d "
                          "total sessions\n" %
                            (self.processed_session_count,
                             self.total_session_count))

        average = sum(self.sizes) / float(len(self.sizes))
        self.stdout.write("Average size was %f bytes\n" % average)

        self.stdout.write("Saw the following keys:\n")
        for key, count in self.keys.iteritems():
            self.stdout.write("    %s (%d times)\n" % (key, count))
