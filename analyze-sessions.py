import time

from collections import defaultdict
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.base import SessionBase

class Command(BaseCommand):
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
            help="Process sessions in batches no larger than BATCH_SIZE"),
        make_option("--sleep-time",
            action='store',
            dest='sleep_time',
            type='float',
            default=2.0,
            help="# of seconds to sleep in between batches"),
        make_option("--ids-from",
            action='store',
            dest='from_file',
            default=None,
            help="Take session_keys from IDS_FROM instead of dynamically generating them with --bigger-than")
    )

    def handle(self, *args, **options):
        self.processed_session_count = 0
        self.total_session_count     = 0
        # [session_size, session_size, ...]
        # accumulated throughout run, then averaged at the end
        self.session_sizes           = []
        # session_key => # of sessions with session_key
        self.session_keys            = defaultdict(int)
        # session_key => [size, size, ...]
        self.session_key_sizes       = defaultdict(list)
        # session_key => total_size
        self.session_key_totals      = defaultdict(int)

        self.process_options(options)

        self.total_session_count = Session.objects.all().count()

        for session in self.get_sessions():
            self.process_session(session)

        self.print_results()

    def process_options(self, options):
        self.batch_size  = options['batch_size']
        self.bigger_than = options['bigger_than']
        self.sleep_time  = options['sleep_time']
        self.verbose     = ('verbosity' in options and
                            int(options['verbosity']) > 1)

        self.file_mode = False
        if options['from_file'] is not None:
            self.file_mode = True
            self.from_file = options['from_file']

        if self.verbose:
            self.stdout.write("analyze-sessions ready\n")
            self.stdout.write("batch size: %d\n" % (self.batch_size))
            self.stdout.write("bigger than: %d\n" % (self.bigger_than))
            self.stdout.write("sleep time: %.2f\n" % (self.sleep_time))
            if self.file_mode:
                self.stdout.write("operating in file mode\n")

    def get_filtered_queryset(self, expire_after=None, ignore_keys=None):
        qs = Session.objects

        if expire_after is not None:
            # handle boundary conditions with identical expire_dates.
            qs = qs.filter(expire_date__gte=expire_after)
            for ikey in ignore_keys:
                qs = qs.exclude(session_key=ikey)

        # XXX: Potentially MySQL-specific. Should be revised to handle
        #      other DBMS, or fail gracefully when they're in use.
        qs = qs.extra(where=['LENGTH(session_data) > %d' % self.bigger_than])

        qs = qs.order_by('expire_date')

        return qs

    def read_ids_from_file(self):
        try:
            f = open(self.from_file, 'r')
        except IOError, e:
            raise CommandError("failed to open input file %s" % self.from_file)

        ids = f.readlines()
        f.close()

        return map(lambda x: x.strip(), ids)

    def get_sessions(self):
        if self.file_mode:
            return self.get_sessions_file()

        return self.get_sessions_db()

    def get_sessions_db(self):
        """
        Return sessions that match the configured bigger than parameters.

        Internally, collect sessions in batches of size batch_size, then yield
        to the caller.
        """
        if self.verbose:
            self.stdout.write("getting sessions dynamically from DB\n")

        # largest expire_date we've seen so far
        max_processed_date = None
        # session_keys for sessions with this expire_date that we've already
        # processed.
        max_processed_keys = []
        while True:
            qs = self.get_filtered_queryset(max_processed_date, max_processed_keys)

            qs = qs[:self.batch_size]

            processed_count = 0
            for session in qs:
                processed_count += 1

                if max_processed_date is None or session.expire_date > max_processed_date:
                    max_processed_date = session.expire_date
                    max_processed_keys = []
                if session.expire_date == max_processed_date:
                    max_processed_keys.append(session.session_key)

                yield session

            if processed_count == 0:
                if self.verbose:
                    self.stdout.write("no more records, exiting\n")

                return

            if self.verbose:
                self.stdout.write("sleeping for %.2f seconds before next batch\n" % self.sleep_time)

            time.sleep(self.sleep_time)

    def get_sessions_file(self):
        if self.verbose:
            self.stdout.write("getting sessions from input file\n")

        keys = self.read_ids_from_file()

        for key in keys:
            try:
                s = Session.objects.get(session_key=key)
                yield s
            except Session.DoesNotExist:
                self.stderr.write("warning: session %s no longer exists. skipping.\n" % key)

    def process_session(self, session):
        self.processed_session_count += 1

        data = session.session_data
        self.session_sizes.append(len(data))

        decoded = session.get_decoded()
        for key, value in decoded.iteritems():
            self.session_keys[key] += 1
            size = self.get_size(key, value)
            self.session_key_sizes[key].append(size)
            self.session_key_totals[key] += size

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

        # Iterate over keys in order of total size (descending), so keys
        # that take up the most space are at the top.
        sorted_items = sorted(self.session_key_totals.items(),
                              cmp=lambda x, y: cmp(x[1], y[1]),
                              reverse=True)
        for key, total in sorted_items:
            count = self.session_keys[key]
            avg_size = sum(self.session_key_sizes[key]) / float(count)
            self.stdout.write("    %s (%d times, avg. size %.2f bytes)\n"
                % (key, count, avg_size))
