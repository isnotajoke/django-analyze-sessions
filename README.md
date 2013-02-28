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
input file (useful for when you want to select sessions on more than
encoded size):

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

## License

Copyright (c) 2013, Kevan Carstensen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met: 

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer. 
2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

## Author

Kevan Carstensen <kevan@isnotajoke.com>
