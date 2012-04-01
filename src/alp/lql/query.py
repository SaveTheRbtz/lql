# vim:fileencoding=utf8

import logging
from operator import itemgetter
from collections import defaultdict
from itertools import islice
from ..errors import *

log = logging.getLogger(__name__)

def where_(where, iterable):
    """Returns only items which pass through ``where`` filter"""
    for dict_ in iterable:
        field, operator, value = where
        if operator(dict_[field], value):
            yield dict_

def select_(fields, iterable):
    """
    Returns only values of given fields from all dicts in iterable

    If tuple of (func, arg) is given then we need to run this function.
    """
    iterable = list(iterable)
    new_fields = []
    for field in fields:
        if isinstance(field, basestring):
            new_fields.append(field)
            continue
        # Yay what a nice function we've got!
        func, arg = field
        func(arg, iterable)
        new_fields.append("{0}({1})".format(func.__name__.upper(), arg))
    filter_func = lambda key: key in new_fields
    # Special handling of SELECT *:
    # We need to return all fields except of hidden ones that starts with '__'
    if '*' in new_fields:
        filter_func = lambda key: not key.startswith('__')
    for row in iterable:
        yield dict((key,value) for key,value in row.items() if filter_func(key))

def group_by_(field, iterable):
    """Group iterable by field"""
    groups = defaultdict(list)
    for dict_ in iterable:
        groups[dict_[field]].append(dict_)
    return ({field: key, "__groups__": value} for key,value in groups.items())

def order_by_(order, iterable):
    """Sort items by field"""
    field, reverse = order
    return sorted(iterable, key=itemgetter(field), reverse=reverse)

class Query():
    """Parses and executes query against list of dictionaries(which can be viewed as a table)"""

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
        try:
            # By default we just return iterable
            result = iterable

            #
            # First step is to filter data
            #
            if 'WHERE' in self.tokens:
                for condition in self.tokens['WHERE']:
                    result = where_(condition, result)
            #
            # Group by
            #
            if 'GROUP BY' in self.tokens:
                result = group_by_(self.tokens['GROUP BY'], result)
            #
            # Select
            #
            result = select_(self.tokens['SELECT'], result)
            #
            # Order by
            #
            if 'ORDER BY' in self.tokens:
                result = order_by_(self.tokens['ORDER BY'], result)
            #
            # Limit
            #
            if 'LIMIT' in self.tokens:
                result = islice(result, self.tokens['LIMIT'])

            return result
        except Exception as e:
            raise ALPLQLUnknownExecutionError(e, "Got an error while executing query. Query most likely malformed.")
