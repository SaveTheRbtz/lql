import os
import random
import unittest

from operator import itemgetter

from ..errors import *
from alp.apache.log_parser import LogEntries
from alp.lql.query import Query

CWD = os.path.dirname(os.path.realpath(__file__))

class TestLQLParser(unittest.TestCase):
    def setUp(self):
        self.entries = LogEntries.from_file(os.path.join(CWD, 'httpd-access-test.log'))

    def test_select(self):
        """Very basic SELECT tests"""
        result = Query("select *").execute(self.entries)
        self.assertEqual(list(self.entries), result)
        result = Query("SELECT ip").execute(self.entries)
        self.assertEqual(list(result), [{key: value} for row in self.entries for key,value in row.items() if key=='IP'])
        result = Query("SELECT ip,TIME").execute(self.entries)
        self.assertEqual(list(result), [{'IP': row['IP'], 'TIME': row['TIME']} for row in self.entries])

    def test_parser_broken_queries(self):
        """Badly broken queries"""
        with self.assertRaises(ALPLQLParserError):
            Query("").execute(self.entries)
        with self.assertRaises(ALPLQLParserError):
            Query("select").execute(self.entries)
        with self.assertRaises(ALPLQLParserError):
            Query("Just 111 Some random staff $*^%$ ").execute(self.entries)
        with self.assertRaises(ALPLQLParserError):
            Query("SELECT TEST(ERROR)").execute(self.entries)

    def test_execution_broken_queries(self):
        """Not so badly broken queries"""
        with self.assertRaises(ALPLQLExecutionError):
            Query("SELECT COUNT(ERROR)").execute(self.entries)
        with self.assertRaises(ALPLQLExecutionError):
            Query("SELECT PERCENT(URL) ORDER BY COUNT(URL)").execute(self.entries)
        with self.assertRaises(ALPLQLExecutionError):
            Query("SELECT TEST ORDER BY COUNT(url)").execute(self.entries)

    def test_where(self):
        """Basic WHERE test"""
        result = Query('select * WHERE ip> "0"').execute(self.entries)
        self.assertEqual(list(self.entries), result)
        result = Query('select * WHERE ip> "0" and ip <="0"').execute(self.entries)
        self.assertEqual(list(result), [])

    def test_order_by(self):
        """Basic ORDER BY tests"""
        result = Query("select * ORDER by url").execute(self.entries)
        self.assertEqual(list(sorted(self.entries, key=itemgetter('URL'), reverse=True)), result)
        result = Query("select * ORDER by  url DESC").execute(self.entries)
        self.assertEqual(list(sorted(self.entries, key=itemgetter('URL'), reverse=True)), result)
        result = Query("select * ORDER by url  ASC").execute(self.entries)
        self.assertEqual(list(sorted(self.entries, key=itemgetter('URL'), reverse=False)), result)

    def test_limit(self):
        """Basic LIMIT tests"""
        result = Query("select * LIMIT 1").execute(self.entries)
        self.assertEqual(list(self.entries)[0], result[0])
        result = Query("select IP LIMIT 10").execute(self.entries)
        self.assertLessEqual(len(list(result)), 10)

    def test_group_by(self):
        """GROUP BY tests"""
        result = Query("select *, COUNT(*) GROUP BY URL ORDER by COUNT(*) LIMIT 1").execute(self.entries)
        result2 = Query("select URL, COUNT(*) GROUP BY URL ORDER by COUNT(*) LIMIT 1").execute(self.entries)
        self.assertEqual(result, result2)
        self.assertEqual(len(list(result)), 1)
        self.assertGreater(result[0]['COUNT(*)'], 0)
        self.assertTrue(all(['URL' in result[0], 'COUNT(*)' in result[0]]))
