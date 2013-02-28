# Django Session Space Analysis Tool

This is a Django management command (as in
https://docs.djangoproject.com/en/dev/howto/custom-management-commands/)
that analyzes and reports on the size of sessions in the DB. It is
intended to make it easier to understand how much space session data
takes up.

## Why?

I noticed that a relatively small number of sessions in my Django app
were consuming 50+KiB of data each, and wanted to understand why.
It isn't feasible or appealing to analyze large numbers of Django
sessions by hand, and I couldn't find any existing tools that did batch
analysis, so I wrote this tool.

## Installation

First, choose an app within your Django environment to host the new
command. Note that the app must be in the INSTALLED_APPS tuple in your
settings file. Then:

```
mkdir -p /path/to/your/app/management/commands
touch /path/to/your/app/management/__init__.py
touch /path/to/your/app/management/commands/__init__.py
cp /path/to/analyze-sessions.py /path/to/your/app/management/commands/analyze-sessions.py
```

You can then run django-admin.py and confirm that the command shows up.

## Example Uses

Break down the space usage of all sessions with more than 15KB of
session data:

```
django-admin.py analyze-sessions --bigger-than=15000
Processed 2 sessions out of 5125 total sessions
Average size was 16885.50 bytes
Saw the following keys:
    foo (2 times, avg. size 15723.00 bytes)
    bar (2 times, avg. size 618.50 bytes)
    baz (2 times, avg. size 211.50 bytes)
```

Break down the space usage of all sessions whose keys are in the given
input file:

```
django-admin.py analyze-sessions --ids-from=/tmp/ids-to-check
Processed 2 sessions out of 5125 total sessions
Average size was 16885.50 bytes
Saw the following keys:
    foo (2 times, avg. size 15723.00 bytes)
    bar (2 times, avg. size 618.50 bytes)
    baz (2 times, avg. size 211.50 bytes)
```

## Known Issues and Bugs

  * The custom WHERE clause used to filter on session size may only work
    on MySQL (I don't have access to a Django installation on another
    DBMS, so I can't vouch for how well it'll work there).
  * The tool could stand to be smarter about size abbreviations (e.g.,
    by learning how to interpret 100KB, or abbreviating output)

## Author

Kevan Carstensen <kevan@isnotajoke.com>
