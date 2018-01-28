from WordDict import WordDict
from Helper import Helper
import unittest
from WordFrequenciesClass import WordFrequencies
from datetime import datetime
import argparse
from io import StringIO
from WordClass import WordClass
import re

class TestUM(unittest.TestCase):
    basicWord = "test"
    markupName = "[!!Dirk|Dirk_Stahlecker!!]"
    wcBasic = WordClass.addWordOrMarkup(basicWord)
    wcMarkup = WordClass.addWordOrMarkup(markupName)

    @classmethod
    def setUpClass(self):
        pass

    @classmethod
    def tearDownClass(self):
        pass

    def test_basicWord(self):
        self.assertEqual(self.basicWord, self.wcBasic.rawWord)
        self.assertTrue(self.wcBasic.toString() == self.basicWord)
        self.assertFalse(self.wcBasic.toString() == self.wcMarkup)

    def test_markupWord(self):
        self.assertEqual(self.markupName, self.wcMarkup.rawWord)
        self.assertTrue("Dirk" == self.wcMarkup.toString())
        self.assertFalse(self.wcMarkup.toString() == self.basicWord)

    def test_differentDisplayNamesForSamePerson(self):
        wcDifferentDisplayName = WordClass.addWordOrMarkup('[!!Dirk_alternate|Dirk_Stahlecker!!]')
        self.assertEqual("Dirk_alternate", wcDifferentDisplayName.toString())
        self.assertEqual(wcDifferentDisplayName, self.wcMarkup)


if __name__ == '__main__':
    unittest.main()