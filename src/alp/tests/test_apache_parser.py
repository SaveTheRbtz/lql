import os
import random
import unittest

from ..errors import *

from alp.apache.log_parser import LogEntries

CWD = os.path.dirname(os.path.realpath(__file__))

class TestParser(unittest.TestCase):
    def setUp(self):
        self.filename = os.path.join(CWD, 'httpd-access-test.log')
        with open(self.filename, 'r', 2**20) as f:
            self.data = f.readlines()

    def test_parsing(self):
        """Parse all lines in file"""
        for line in self.data[1:]:
            LogEntries.parse_line(line, LogEntries.default_format)

    def test_parsing_error(self):
        """On broken lines parser should throw ALPApacheParserError"""
        self.assertRaises(ALPApacheParserError, LogEntries.parse_line, self.data[0], LogEntries.default_format)

    def test_full_parsing(self):
       """class method from_file() should coupe with broken files"""
       self.assertNotEqual(LogEntries.from_file(self.filename), None)
