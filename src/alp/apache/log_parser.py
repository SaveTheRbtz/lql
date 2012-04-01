# vim:fileencoding=utf8

import re
import logging

from ..errors import *
from collections import namedtuple

log = logging.getLogger(__name__)

class LogEntries(object):
    __doc__ = """This is comtainer for parsed log files"""

    # "Combined" log format from https://httpd.apache.org/docs/2.4/logs.html
    # ``time`` is taken without timezone 
    # FIXME: method/protocol/url could be unavailable if request is too large or broken (414/404)
    default_format = r'(?P<IP>[0-9.:a-f]+) (?P<IDENT>[^ ]+) (?P<USER>[^ ]+) \[(?P<TIME>[^ ]+) [+-][0-9]{4}\] "(?P<METHOD>[A-Z]+) ' + \
                     r'(?P<URL>.+?) (?P<PROTOCOL>.+?)" (?P<CODE>[0-9]+) (?P<SIZE>[-0-9]+) "(?P<REFERER>.+)" "(?P<USERAGENT>.+)"$'

    def __init__(self, entries=None):
        self.entries = entries

    def __iter__(self):
        return iter(self.entries)

    @staticmethod
    def parse_line(line, log_format):
        """
        Parses one single ``line`` according to ``log_format``. Returns
        namedtuple.

            Dear Santa, I've been a veeeewwy good boy this year, so please
            write an apache/nginx module that saves logs in json/xml!

        TODO: Also there are many ways to optimize this. For example: do not
        use regexps!
        """
        try:
            return re.match(log_format, line).groupdict()
        except Exception as e:
            raise ALPApacheParserError(e, "Can't parse line: {0}".format(line))

    @classmethod
    def from_file(cls, filename, log_format=None):
        """
        Loads log entries from ``filename`` with format specified in
        ``log_format`` regular exception. By default "combined" log format is
        used.

        TODO: We can try applying WHERE filters before parsing line if it's
        possible.
        TODO: Also some optimizations needed for multi-gigabyte logs like
        binary search.
        """
        if log_format is None:
            log_format = LogEntries.default_format
        try:
            parsed, failed = 0, 0
            with open(filename, 'r', 2**20) as lines:
                entries = []
                log.debug("Log parsing started")
                for line in lines:
                    try:
                        entries.append(LogEntries.parse_line(line, log_format))
                        parsed += 1
                    except ALPApacheParserError as e:
                        failed += 1
                        log.debug(e)
                log.debug("Log parsing finished")
                log.info("Parsed [ {0} ]. FAILED [ {1} ]".format(parsed, failed))
                return cls(entries)
        except EnvironmentError as e:
            raise ALPApacheImportError(e, "Can't open file: {0}".format(filename))
