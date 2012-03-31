# vim:fileencoding=utf8

import logging
from operator import itemgetter, contains
from collections import defaultdict
from ..errors import *
import logging as log

log = logging.getLogger(__name__)

def select_(fields, iterable):
    """Returns only values of given fields from all dicts in iterable"""
    for row in iterable:
        yield dict((key,value) for key,value in row.items() if key in fields)

def where_(where, iterable):
    """Returns only items which pass through ``where`` filter"""
    for dict_ in iterable:
        field, operator, value = where
        if operator(dict_[field], value):
            yield dict_

def group_by_(field, iterable):
    """Group by iterable by field"""
    # XXX:
    groups = defaultdict(list)
    for dict_ in iterable:
        groups[dict_[field]].append(dict_)
    return groups

def order_by_(order, iterable):
    """Sort items by field"""
    field, reverse = order
    return sorted(iterable, key=itemgetter(field), reverse=reverse)

class Query():
    __doc__ = """XXX:"""

    def __init__(self, query):
        """Init object with specific query"""
        from .parser import Parser
        try:
            self.parser = Parser()
            self.tokens = self.parser(query)
        except ALPLQLParserError as e:
            raise ALPLQLParserError(e, "Query [ {0} ] can't be parssed".format(query))
        except Exception as e:
            raise ALPLQLUnknownParserError(e, "Error occured during parsing of [ {0} ] ".format(query))

    def execute(self, iterable):
        """
        Run query against all rows in table.

        This whole thing should look beautiful if written in functional style
        but it will render it unreadable for most of people... maybe for me too =)
        """
        # By default we just return iterable
        result = iterable

        #
        # First step is to filter data
        #
        if 'WHERE' in self.tokens:
            for condition in self.tokens['WHERE']:
                result = where_(condition, result)

        #
        # Order output if it was requested
        #
        if 'ORDER BY' in self.tokens:
            result = order_by_(self.tokens['ORDER BY'], result)
        #
        # Limiting is not of the last steps
        #
        if 'LIMIT' in self.tokens:
            result = result[:self.tokens['LIMIT']]
        #
        # Final step is to output only filds that were requested
        #
        result = select_(self.tokens['SELECT'], result)

        return result
