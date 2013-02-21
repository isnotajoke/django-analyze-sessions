from collections import defaultdict
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.base import SessionBase

class Command(BaseCommand):
    args = '--batch-size=n --bigger-than=n'
    help = "Analyze Django sessions, summarizing present keys & session size"

    option_list = BaseCommand.option_list + (
        make_option("--bigger-than",
            action='store',
            dest='bigger_than',
            type='int',
            default=10*1024,
            help="Only return records with more than BIGGER_THAN bytes"),
        make_option("--batch-size",
            action='store',
            dest='batch_size',
            type='int',
            default=5000,
            help="Process sessions in batches no larger than BATCH_SIZE")
    )

    def handle(self, *args, **options):
        self.processed_session_count = 0
        self.total_session_count     = 0
        self.session_sizes           = []
        self.session_keys            = defaultdict(int)
        self.session_key_sizes       = defaultdict(list)

        self.process_options(options)

        self.total_session_count = Session.objects.all().count()

        for session in self.get_sessions():
            self.process_session(session)

        self.print_results()

    def process_options(self, options):
        self.batch_size = options['batch_size']
        self.bigger_than = options['bigger_than']

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
        self.processed_session_count += 1

        data = session.session_data
        self.session_sizes.append(len(data))

        decoded = session.get_decoded()
        for key, value in decoded.iteritems():
            self.session_keys[key] += 1
            self.session_key_sizes[key].append(self.get_size(key, value))

    def get_size(self, key, value):
        """
        Serialize an object hierarchy & return the size of the result.
        """
        d = {key: value}
        d_enc = SessionBase().encode(d)
        return len(d_enc)

    def print_results(self):
        self.stdout.write("Processed %d sessions out of %d "
                          "total sessions\n" %
                            (self.processed_session_count,
                             self.total_session_count))

        if self.session_sizes:
            average = sum(self.session_sizes) / float(len(self.session_sizes))
        else:
            average = 0.0

        self.stdout.write("Average size was %.2f bytes\n" % average)

        self.stdout.write("Saw the following keys:\n")
        for key, count in self.session_keys.iteritems():
            avg_size = sum(self.session_key_sizes[key]) / float(count)
            self.stdout.write("    %s (%d times, avg. size %.2f bytes)\n"
                % (key, count, avg_size))
