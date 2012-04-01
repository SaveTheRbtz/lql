# vim:fileencoding=utf8

from optparse import OptionParser

def getopt():
    """
    Parses options via OptionParser, constructs help message and retruns 
    ``parse_args()`` result.
    """
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename", 
                      default="/var/log/httpd-access.log",
                      help="access log FILE (default: %default)", metavar="FILE")
    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=None,
                      help="Be verbose (default: %default)")
    parser.usage = usage.__doc__

    return parser.parse_args()

def usage():
    r"""%prog -f /path/to/httpd-access.log [-v] [-f ...] 'LQL QUERY'

About
=====
This program tries to emulate some SQL features by providing tiny subset of
it to process apache/nginx ``combined`` log format.

Actually optimal solution for this problem is to put data to agregation
servers, move it to Hadoop/HBASE (or equivalent) and then use pig/hive to make
queries to multi-terabyte datasets in nearly realtime (instead of reinventing
the wheel). But assignment is an assigment.

Cheating
========
Of course there was a SQL-way of solving this problem: just parse data, put it
in some kind of relational storage(even sqlite will be sufficient) and run some
queries against it.  Also this task is easilly accomplished by ``awk`` or even
Linux's ``coreutils``.

But I think purpose of this task was to evaluate my Python/Programming skills
not to see my Mad-SQL/awk/Shell-skilz.

Speed
=====
Perfomance was not a concern in this application. Preference was given to
readability of code. If I wanted it to be fast I should have just used
MapReduce as it was described above.

LQL
===
This is small log processing sublanguage inspired by SQL. Very limited, for
example it does not support table schemes and indexes, but anyway it does
it's job.

Right way to do this was implementing small subset of relational model along
with tuple calculus. But it's imposible for me to do it in two days.
Also my tokenizer/parser implementation is very-very limited. It not even close
to LR parser based on lex/yacc or PLY library.
But anyway it was fun to implement such project in such a small time.

Examples
========
Print up to 10 hits between 10/Mar/2012:04:28:08 and 10/Mar/2012:04:29:08
ordered by ip::

    ./lql -f alp/tests/httpd-access-test.log -v \
            'SELECT url,time WHERE time > "10/Mar/2012:04:28:08" and time <=
                "10/Mar/2012:04:29:08" ORDER BY ip ASC LIMIT 10'

Produce list of requests which URLs contains word siteops::

    SELECT * where url CONTAINS "siteops"

Produce the minimum, maximum, and average CPU for a configurable time segment.
For example if asked for the these numbers for a 5-minute time period, print
the QPS numbers for 00:00 to 00:04, 00:05 to 00:19, 00:10 to 00:14, and so on::

    TODO:

Produce a list of the URLs called and the average QPS of those URLs::

    TODO:

Produce a list of the top 10 requestors::

    SELECT IP,COUNT(IP) GROUP BY IP ORDER BY COUNT(IP) LIMIT 10

Produce a list of errors (4xx and 5xx status codes) by URL and their call
count::

    SELECT URL,COUNT(URL) WHERE CODE >= "400" AND CODE < "600"
        GROUP BY URL ORDER BY COUNT(URL)

Produce a percentage report of request types, for example GET, PUT, etc::

    SELECT METHOD, PERCENT(METHOD) GROUP BY METHOD ORDER BY PERCENT(METHOD)

Produce a percentage report of response types (200 vs 404 vs 500, etc)::

    SELECT CODE, PERCENT(CODE) GROUP BY CODE ORDER BY PERCENT(CODE)

Bonus Task
==========
    Allow for the script to work on a constantly updating file. The user
    would specify that a report should be generated every N minutes. For
    example, if a user said the 5 minutes, the operation listed above would
    print its report over the last 5 minutes, every 5 minutes.

It's easy to implement but I'd better spend this time to write unittests and
docs.
"""
    pass
