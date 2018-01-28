from WordDict import WordDict
from Helper import Helper
import unittest
from WordFrequenciesClass import WordFrequencies
from datetime import datetime
import argparse
from io import StringIO
import sys

date = Helper.makeDateObject('10-12-17')

class TestUM(unittest.TestCase):
    wd = WordDict()

    @classmethod
    def setUpClass(self):
        self.wd.addWord('word1', 1, date, date, False)
        self.wd.addWord('word2', 1, date, date, False)
        self.wd.addWord('word3', 1, date, date, False)

    @classmethod
    def tearDownClass(self):
        pass

    def test_addWordNoConflicts(self):
        self.assertEqual(self.wd.getCount('word1'), 1)
        self.assertEqual(self.wd.getFirstOccurrence('word1'), date)

    def test_incrementCount(self):
        self.wd.incrementCount('word1')
        self.assertEqual(self.wd.getCount('word1'), 2)

    # def test_addWordConflicts(self):

    def test_exists(self):
        self.assertTrue(self.wd.exists('word1'))
        self.assertTrue(self.wd.exists('word2'))
        self.assertFalse(self.wd.exists('wordthatdoesntexist'))


if __name__ == '__main__':
    unittest.main()