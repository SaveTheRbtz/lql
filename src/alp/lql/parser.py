# vim:fileencoding=utf8

import re
import logging

from collections import defaultdict
from operator import contains, ge, gt, le, lt, eq, ne
from .query import select_, where_, order_by_, group_by_
from ..errors import *

log = logging.getLogger(__name__)

import functions

class Parser(object):
    __doc__ = """
        This is pretty limited and rather hackish tokenizer+parser
        """

    STATEMENT  = r'[A-Z(*)]+'
    STATEMENTS = r'[A-Z(*),]+'
    NUMBER     = r'[0-9]+'
    STRING     = r'".*?"'

    TOKEN_LIST = ['SELECT', 'WHERE', 'GROUP BY', 'ORDER BY', 'LIMIT']
    ANY_TOKEN  = r'\s?(?:' + r'|'.join(TOKEN_LIST) + r')?'

    TOKENS = {
                'SELECT': r'SELECT\s+({stmts})'.format(stmts=STATEMENTS),
                'WHERE':  r'(?:WHERE|AND)\s+({stmt})\s*([><=]+|CONTAINS)\s*({number}|{string})'.format(stmt=STATEMENT,
                                                                                         string=STRING,
                                                                                         number=NUMBER),
                'GROUP BY': r'GROUP\s+BY\s+({stmt})'.format(stmt=STATEMENT),
                'ORDER BY': r'ORDER\s+BY\s+({stmt})\s*(ASC|DESC)?'.format(stmt=STATEMENT),
                'LIMIT': r'LIMIT\s({number})'.format(number=NUMBER),
            }
    @staticmethod
    def normalize(query):
        """
            Strips ``query`` and converts to uppercase

            XXX: TESTS!
        """
        normalized_query = ""
        inside_quotes = False
        for c in query:
            if c == '"':
                inside_quotes = not inside_quotes
            if not inside_quotes:
                # Skip spaces after ',' and double spaces
                if normalized_query and normalized_query[-1] in [',', ' '] and c == ' ':
                    continue
                normalized_query += c.upper()
            else:
                normalized_query += c
        if inside_quotes:
            raise ALPLQLParserError("There is odd number of double quotes inside query")
        return normalized_query.strip()

    def __call__(self, query):
        """
        This method parses given string and returns dict of tokens with
        parameters from it along with their arguments

        This is the most complicated (don't confuse with complex) method in
        whole ALP.

        Most likely it's error prone. But I've tried to do it as robust as I
        could.

        Yet again it's better not to reinvert the wheel an use for example
        David Beazeley's PLY

        PS. Kids, never ever ever try to parse Chomsky Type 2 grammar (context
        free grammar) with Chomsky Type 3 grammar (regular expression) - It's
        just impossible. But it's fun to try =)

        XXX: TESTS!
        """
        tokens = defaultdict(list)

        #
        # First we need to normalize our query
        #
        log.debug("Original query:   {0}".format(query))
        query = self.normalize(query)
        log.debug("Normalized query: {0}".format(query))

        #
        # Then we run sainity checks on query
        #

        if not len(query):
            log.warning("No query given")
            return tokens

        # All queries should start with SELECT
        if not query.startswith('SELECT'):
            log.error("No SELECT detected: {0}".format(query))
            return tokens

        #
        # Then we match all tokens
        #
        for token, regexp in self.TOKENS.items():
            real_regexp = regexp + self.ANY_TOKEN
            found = re.findall(real_regexp, query)
            log.debug("Running regexp: {0}".format(real_regexp))
            for match in found:
                log.debug("Match for token [ {0} ] is [ {1} ]".format(token, match))
                if token == 'SELECT':
                    if tokens[token]:
                        raise ALPLQLParserError("Can't parse a request: two SELECTs found: [ {0} ] and [ {1} ]".format(tokens[token], match))
                    #
                    # Replace LQL functions with their Python implementations
                    #
                    matches = []
                    for field in match.split(','):
                        func = re.match(r'([A-Z]+)\((.*)\)', field)
                        if func:
                            name, arg = func.groups()
                            log.debug("Found function call: [ {0} ]".format(name))
                            try:
                                matches.append((getattr(functions, name.lower()), arg))
                            except AttributeError:
                                raise ALPLQLParserError("Unknown function: [ {0} ]".format(name))
                        else:
                            matches.append(field)

                    tokens[token] = matches
                elif token == 'WHERE':
                    # Map string LQL to Python functions
                    op_map = {
                                '>=': ge,
                                '<=': le,
                                '>':  gt,
                                '<':  lt,
                                '=':  eq,
                                '==': eq,
                                '!=': ne,
                                '<>': ne,
                                'CONTAINS': contains,
                            }
                    field, op, value = match

                    # If it's starts with double quotes - it's string
                    if value.startswith('"'):
                        value = value.strip('"')
                    else:
                        try:
                            value = int(value)
                        except Exception:
                            raise ALPLQLParserError("Unknown token: [ {0} ]".format(value))
                    # Replace operator with function alternatives
                    try:
                        op = op_map[op]
                    except KeyError:
                        raise ALPLQLParserError("Unknown token: [ {0} ]".format(op))
                    tokens[token].append((field, op, value))
                elif token == 'LIMIT':
                    tokens[token] = int(match)
                elif token == 'ORDER BY':
                    field, order = match
                    if order == 'DESC':
                        order = False
                    tokens[token] = field, not order
                else:
                    tokens[token] = match
        log.info("Resulting tokens: {0}".format(tokens))
        return tokens
